import json
import tempfile
import unittest
from pathlib import Path

from openmaxfire.monitor import (
    JsonlMonitorRecorder,
    MonitorState,
    format_monitor_summary,
    replay_capture,
)
from openmaxfire.protocol import AddressedResponse, TelemetryResponse


def addressed(address: int, value: int) -> AddressedResponse:
    raw = f"CR{address:02x}{value:02x}".encode("ascii")
    return AddressedResponse("C", "R", address, value, raw)


class MonitorStateTests(unittest.TestCase):
    def test_indicator_hold_must_be_positive_and_finite(self):
        for value in (0, -1, float("inf"), float("nan"), True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    MonitorState(format04_indicator_hold=value)

    def test_snapshot_preserves_raw_values_and_decodes_evidence_backed_fields(self):
        state = MonitorState(stale_after=10.0)
        observed = 1_000_000_000
        for frame in (
            addressed(0x01, 0x04),
            addressed(0x02, 0x52),
            addressed(0x06, 0x07),
            addressed(0x08, 0x04),
            addressed(0x09, 0x78),
            addressed(0x0A, 0x49),
            TelemetryResponse(0x03, (0x78,), b"T0378"),
            TelemetryResponse(0x04, (0x49,), b"T0449"),
            TelemetryResponse(0x08, (0x1F,), b"T081f"),
            TelemetryResponse(0x09, (0x4B,), b"T094b"),
            TelemetryResponse(0x0A, (0x12, 0x34), b"T0a1234"),
            TelemetryResponse(0x0C, (0x08,), b"T0c08"),
        ):
            state.observe(
                frame,
                monotonic_ns=observed,
                created_utc="2026-08-22T20:00:00+00:00",
            )

        snapshot = state.snapshot(
            now_monotonic_ns=2_000_000_000,
            generated_utc="2026-08-22T20:00:01+00:00",
        )
        self.assertTrue(snapshot["fresh"])
        self.assertEqual(snapshot["controller_registers"]["CR02"], "52")
        self.assertEqual(snapshot["telemetry_bytes"]["T0B"], "34")
        self.assertEqual(snapshot["telemetry_words"]["T0A/T0B"]["value"], 0x1234)

        decoded = snapshot["decoded"]
        self.assertTrue(decoded["panel_buttons"]["up"])
        self.assertTrue(decoded["physical_inputs"]["ash_drawer_open"])
        self.assertFalse(decoded["physical_inputs"]["firebox_door_open"])
        self.assertTrue(decoded["thermostat_open"])
        self.assertNotIn("operating_state", decoded)
        self.assertNotIn("bixcheck_55_igniter_display", decoded)
        self.assertTrue(decoded["warning_flash_bits"]["firebox_door"])
        self.assertTrue(decoded["warning_flash_bits"]["ash_drawer"])
        self.assertFalse(decoded["warning_flash_bits"]["feeder_wheel"])
        self.assertEqual(decoded["fault_indicators"]["active_mask"], "1F")
        self.assertEqual(decoded["fault_indicators"]["lights"], [1, 2, 3, 4, 5])
        self.assertIsNone(decoded["fault_indicators"]["fault_code"])
        self.assertEqual(decoded["format04_live_correlations"]["fan_pot_raw"], 0x78)
        self.assertEqual(decoded["format04_live_correlations"]["feed_pot_raw"], 0x49)
        self.assertEqual(
            decoded["format04_live_correlations"]["t09_meaning_unresolved_raw"],
            0x4B,
        )
        self.assertEqual(decoded["format04_state_candidate"]["code"], "unclassified")
        self.assertFalse(
            decoded["format04_state_candidate"]["control_verification_eligible"]
        )

        summary = format_monitor_summary(snapshot)
        self.assertIn("drawer=open", summary)
        self.assertIn("fan-pot=120", summary)
        self.assertIn("door-warning=on", summary)
        self.assertIn("drawer-warning=on", summary)

    def test_later_format_uses_recovered_bixcheck_state_and_igniter_display(self):
        state = MonitorState()
        state.observe(addressed(0x08, 0x07), monotonic_ns=1)
        state.observe(TelemetryResponse(0x08, (0x07,), b"T0807"), monotonic_ns=2)
        state.observe(TelemetryResponse(0x09, (0x4B,), b"T094b"), monotonic_ns=3)
        decoded = state.snapshot(now_monotonic_ns=3)["decoded"]
        self.assertEqual(decoded["operating_state"]["label"], "TSTAT L 4")
        self.assertEqual(decoded["bixcheck_55_igniter_display"]["label"], "L R good")

    def test_format04_fault_indicator_survives_dark_flash_phase_then_clears(self):
        state = MonitorState(format04_indicator_hold=8.0)
        state.observe(addressed(0x08, 0x04), monotonic_ns=0)
        state.observe(TelemetryResponse(0x08, (0x80,), b"T0880"), monotonic_ns=0)
        state.observe(
            TelemetryResponse(0x08, (0x00,), b"T0800"),
            monotonic_ns=7_000_000_000,
        )

        dark_phase = state.snapshot(now_monotonic_ns=7_000_000_000)["decoded"]
        self.assertEqual(dark_phase["fault_indicators"]["instantaneous_raw"], "00")
        self.assertEqual(dark_phase["fault_indicators"]["active_mask"], "80")
        self.assertEqual(
            dark_phase["fault_indicators"]["fault_code"],
            "feeder_wheel_failure",
        )
        self.assertTrue(dark_phase["warning_flash_bits"]["feeder_wheel"])

        state.observe(
            TelemetryResponse(0x08, (0x00,), b"T0800"),
            monotonic_ns=9_000_000_000,
        )
        cleared = state.snapshot(now_monotonic_ns=9_000_000_000)["decoded"]
        self.assertEqual(cleared["fault_indicators"]["active_mask"], "00")
        self.assertEqual(cleared["fault_indicators"]["lights"], [])
        self.assertFalse(cleared["warning_flash_bits"]["feeder_wheel"])

    def test_later_format_exposes_raw_bixcheck_alarm_without_format04_decode(self):
        state = MonitorState()
        state.observe(addressed(0x08, 0x07), monotonic_ns=1)
        state.observe(TelemetryResponse(0x13, (0xA5,), b"T13a5"), monotonic_ns=2)
        decoded = state.snapshot(now_monotonic_ns=2)["decoded"]
        self.assertEqual(decoded["alarm_status"]["source"], "T13")
        self.assertEqual(decoded["alarm_status"]["raw"], "A5")
        self.assertFalse(decoded["alarm_status"]["decoded"])
        self.assertNotIn("fault_indicators", decoded)

    def test_snapshot_marks_missing_or_old_data_stale(self):
        empty = MonitorState(stale_after=2.0).snapshot(now_monotonic_ns=0)
        self.assertTrue(empty["stale"])
        self.assertIsNone(empty["age_seconds"])

        state = MonitorState(stale_after=2.0)
        state.observe(addressed(0x00, 0), monotonic_ns=1_000_000_000)
        snapshot = state.snapshot(now_monotonic_ns=3_000_000_000)
        self.assertTrue(snapshot["stale"])
        self.assertEqual(snapshot["age_seconds"], 2.0)

    def test_recorder_refuses_silent_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "monitor.jsonl"
            recorder = JsonlMonitorRecorder(path, metadata={"read_only": True})
            recorder.record(MonitorState().snapshot(now_monotonic_ns=0))
            recorder.close()
            with self.assertRaises(FileExistsError):
                JsonlMonitorRecorder(path)
            events = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(events[0]["event"], "session")
            self.assertEqual(events[1]["event"], "snapshot")


class CaptureReplayTests(unittest.TestCase):
    def test_replay_resynchronizes_after_partial_malformed_opening_line(self):
        events = [
            {
                "schema": "openmaxfire.serial-capture.v1",
                "event": "session",
                "metadata": {"baudrate": 9600},
            },
            {
                "event": "traffic",
                "direction": "tx",
                "data_hex": "43 52 30 38",
                "monotonic_ns": 1,
            },
            {
                "event": "traffic",
                "direction": "rx",
                "data_hex": "30 66 0A 54 30 39",
                "created_utc": "2026-08-22T20:00:00+00:00",
                "monotonic_ns": 2,
            },
            {
                "event": "traffic",
                "direction": "rx",
                "data_hex": "34 62 0A 43 52 30 38 30 34 0A 54 30 38 31 38 0A",
                "created_utc": "2026-08-22T20:00:01+00:00",
                "monotonic_ns": 3,
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.jsonl"
            path.write_text("".join(json.dumps(item) + "\n" for item in events))
            replay = replay_capture(path)

        self.assertEqual(replay.malformed_lines, 1)
        self.assertEqual(replay.parsed_frames, 3)
        self.assertEqual(replay.trailing_bytes, b"")
        self.assertEqual(replay.session_metadata["baudrate"], 9600)
        snapshot = replay.state.snapshot(now_monotonic_ns=3, source="replay")
        self.assertEqual(snapshot["controller_registers"]["CR08"], "04")
        self.assertNotIn("operating_state", snapshot["decoded"])
        self.assertEqual(
            snapshot["decoded"]["format04_live_correlations"]["t09_meaning_unresolved_raw"],
            0x4B,
        )
        self.assertTrue(snapshot["decoded"]["warning_flash_bits"]["firebox_door"])

    def test_preserved_format04_captures_replay_with_observed_correlations(self):
        captures = (
            Path(__file__).resolve().parents[1]
            / "research"
            / "live"
            / "2026-08-22-fw202-format04"
            / "captures"
        )
        cases = {
            "fw202-identify-all-closed-long.jsonl": (False, False, False),
            "fw202-identify-firebox-door-open-long.jsonl": (True, False, False),
            "fw202-identify-ash-drawer-open-long.jsonl": (False, True, False),
            "fw202-identify-thermostat-open-long.jsonl": (False, False, True),
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                replay = replay_capture(captures / name)
                snapshot = replay.state.snapshot(
                    now_monotonic_ns=replay.last_monotonic_ns or 0,
                    source="replay",
                )
                decoded = snapshot["decoded"]
                format04 = decoded["format04_live_correlations"]
                observed = (
                    decoded["warning_flash_bits"]["firebox_door"],
                    decoded["warning_flash_bits"]["ash_drawer"],
                    format04["thermostat_open"],
                )
                self.assertEqual(observed, expected)
                self.assertEqual(snapshot["controller_registers"]["CR08"], "04")
                self.assertEqual(format04["t09_meaning_unresolved_raw"], 0x07)

    def test_preserved_fault8_capture_retains_alarm_across_final_dark_phase(self):
        capture = (
            Path(__file__).resolve().parents[1]
            / "research"
            / "live"
            / "2026-08-23-fw202-control-faults"
            / "captures"
            / "fw202-fault8-traffic.jsonl"
        )
        replay = replay_capture(capture)
        snapshot = replay.state.snapshot(
            now_monotonic_ns=replay.last_monotonic_ns or 0,
            source="replay",
        )
        fault = snapshot["decoded"]["fault_indicators"]

        self.assertEqual(replay.parsed_frames, 351)
        self.assertEqual(replay.malformed_lines, 0)
        self.assertEqual(snapshot["telemetry_bytes"]["T08"], "00")
        self.assertEqual(snapshot["telemetry_bytes"]["T13"], "BA")
        self.assertEqual(fault["instantaneous_raw"], "00")
        self.assertEqual(fault["active_mask"], "80")
        self.assertEqual(fault["lights"], [8])
        self.assertEqual(fault["fault_code"], "feeder_wheel_failure")
        self.assertTrue(snapshot["decoded"]["warning_flash_bits"]["feeder_wheel"])

    def test_replay_exposes_configurable_indicator_hold(self):
        capture = (
            Path(__file__).resolve().parents[1]
            / "research"
            / "live"
            / "2026-08-22-fw202-format04"
            / "captures"
            / "fw202-identify-door-open.jsonl"
        )
        replay = replay_capture(capture, format04_indicator_hold=12.5)
        self.assertEqual(replay.state.format04_indicator_hold, 12.5)


if __name__ == "__main__":
    unittest.main()
