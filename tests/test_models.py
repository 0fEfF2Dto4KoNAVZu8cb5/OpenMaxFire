import unittest

from openmaxfire.monitor import MonitorState
from openmaxfire.protocol import AddressedResponse, TelemetryResponse


def addressed(address, value):
    return AddressedResponse("C", "R", address, value, f"CR{address:02x}{value:02x}".encode())


class TypedSnapshotTests(unittest.TestCase):
    def test_later_profile_decodes_documented_measurements(self):
        state = MonitorState(stale_after=10)
        for address, value in {
            0x00: 0,
            0x01: 4,
            0x02: 0x24,
            0x06: 4,
            0x08: 7,
            0x0B: 2,
            0x0C: 0x71,
            0x0D: 0,
            0x0E: 0,
        }.items():
            state.observe(addressed(address, value), monotonic_ns=1)
        for frame in (
            TelemetryResponse(0x00, (0xFE,), b"T00fe"),
            TelemetryResponse(0x02, (0xFF,), b"T02ff"),
            TelemetryResponse(0x04, (10,), b"T040a"),
            TelemetryResponse(0x08, (7,), b"T0807"),
            TelemetryResponse(0x09, (0x4B,), b"T094b"),
            TelemetryResponse(0x0A, (0x12, 0x34), b"T0a1234"),
            TelemetryResponse(0x0E, (0x00, 0x78), b"T0e0078"),
            TelemetryResponse(0x10, (0x00, 0x78), b"T100078"),
            TelemetryResponse(0x13, (0xA5,), b"T13a5"),
        ):
            state.observe(frame, monotonic_ns=1)

        snapshot = state.typed_snapshot(now_monotonic_ns=2)
        self.assertEqual(snapshot.profile_key, "fw271-format07")
        self.assertEqual(snapshot.telemetry.board_temperature_c, -2)
        self.assertEqual(snapshot.telemetry.board_temperature_f, 29)
        self.assertEqual(snapshot.telemetry.fan_trim_percent, 30)
        self.assertEqual(snapshot.telemetry.exhaust_fan_rpm, 240)
        self.assertEqual(snapshot.telemetry.ash_level, 0x1234)
        self.assertEqual(snapshot.telemetry.feed_cycle_seconds, 2.0)
        self.assertEqual(snapshot.target_heat_level, 4)
        self.assertTrue(snapshot.operating_state.thermostat)
        self.assertEqual(snapshot.alarms.raw, 0xA5)
        self.assertEqual(snapshot.alarms.raw_source, "T13")
        self.assertIsNone(snapshot.alarms.indicator_active_mask)
        self.assertIsNone(snapshot.alarms.indicator_hold_seconds)

    def test_format04_does_not_treat_t09_as_state_without_t0c(self):
        state = MonitorState()
        for address, value in {
            0x00: 0,
            0x08: 4,
            0x0B: 2,
            0x0C: 2,
            0x0D: 0,
            0x0E: 0,
        }.items():
            state.observe(addressed(address, value), monotonic_ns=1)
        state.observe(TelemetryResponse(0x08, (0x18,), b"T0818"), monotonic_ns=1)
        state.observe(TelemetryResponse(0x09, (0x4B,), b"T094b"), monotonic_ns=1)
        typed = state.typed_snapshot(now_monotonic_ns=1)
        self.assertIsNone(typed.operating_state)
        self.assertEqual(typed.telemetry.format04_t09_raw, 0x4B)
        self.assertEqual(typed.telemetry.format04_state_unresolved_raw, 0x4B)
        self.assertEqual(typed.format04_state_candidate.code, "unclassified")
        self.assertFalse(
            typed.format04_state_candidate.control_verification_eligible
        )
        self.assertTrue(typed.alarms.firebox_door_warning)
        self.assertTrue(typed.alarms.ash_drawer_warning)
        self.assertFalse(typed.alarms.feeder_wheel_warning)
        self.assertEqual(typed.alarms.indicator_source, "T08")
        self.assertEqual(typed.alarms.indicator_active_mask, 0x18)
        self.assertEqual(typed.alarms.indicator_lights, (4, 5))
        self.assertIsNone(typed.alarms.fault_code)

    def test_format04_t0c_decodes_exact_state_family_and_ignores_t15(self):
        for t0c, t15, expected in (
            (0x20, 0x0F, "off"),
            (0x28, 0x00, "off"),
            (0x30, 0x08, "prefill"),
            (0x38, 0xFF, "prefill"),
        ):
            with self.subTest(t0c=t0c, t15=t15):
                state = MonitorState()
                for address, value in {
                    0x00: 0,
                    0x08: 4,
                    0x0B: 2,
                    0x0C: 2,
                    0x0D: 0,
                    0x0E: 0,
                }.items():
                    state.observe(addressed(address, value), monotonic_ns=1)
                state.observe(
                    TelemetryResponse(0x09, (0x07,), b"T0907"), monotonic_ns=1
                )
                state.observe(
                    TelemetryResponse(0x0C, (t0c,), b"T0c"), monotonic_ns=1
                )
                state.observe(
                    TelemetryResponse(0x15, (t15,), b"T15"), monotonic_ns=1
                )
                typed = state.typed_snapshot(now_monotonic_ns=1)
                self.assertEqual(typed.operating_state.phase, expected)
                self.assertEqual(typed.telemetry.format04_state_raw, t0c)
                self.assertEqual(typed.format04_state_candidate.code, expected)
                self.assertTrue(
                    typed.format04_state_candidate.control_verification_eligible
                )
                self.assertFalse(typed.format04_state_candidate.t09_discriminating)

    def test_format04_t0c_exposes_operating_level(self):
        state = MonitorState()
        for address, value in {
            0x00: 0,
            0x08: 4,
            0x0B: 2,
            0x0C: 2,
            0x0D: 0,
            0x0E: 0,
        }.items():
            state.observe(addressed(address, value), monotonic_ns=1)
        state.observe(TelemetryResponse(0x0C, (0x4B,), b"T0c4b"), monotonic_ns=1)
        typed = state.typed_snapshot(now_monotonic_ns=1)
        self.assertEqual(typed.operating_state.phase, "operating")
        self.assertEqual(typed.current_heat_level, 4)
        self.assertEqual(typed.target_heat_level, 4)
        self.assertTrue(typed.operating_state.thermostat)


if __name__ == "__main__":
    unittest.main()
