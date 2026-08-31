import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


TOOL_PATH = Path(__file__).parents[1] / "tools" / "live_validation_session.py"
SPEC = importlib.util.spec_from_file_location("live_validation_session", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
live_validation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = live_validation
SPEC.loader.exec_module(live_validation)


class LiveValidationToolTests(unittest.TestCase):
    def test_evidence_backed_mask_and_range_evaluation(self):
        door_open = live_validation.Interaction(
            "door", "Door", "", 0x02, expected=0x20, mask=0x20
        )
        self.assertEqual(live_validation._evaluate([0x32, 0x72], door_open)[0], "pass")
        self.assertEqual(live_validation._evaluate([0x12], door_open)[0], "fail")

        centered = live_validation.Interaction(
            "pot", "Pot", "", 0x09, minimum=0x60, maximum=0x90
        )
        self.assertEqual(live_validation._evaluate([0x78, 0x79], centered)[0], "pass")
        self.assertEqual(live_validation._evaluate([0xFF], centered)[0], "fail")

    def test_simulated_automatic_run_writes_complete_evidence(self):
        parser = live_validation.build_parser()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "session"
            args = parser.parse_args(
                [
                    "--simulate",
                    "--output-dir",
                    str(output),
                    "--identity-repeats",
                    "2",
                    "--snapshot-cycles",
                    "1",
                    "--eeprom-copies",
                    "1",
                    "--request-delay",
                    "0",
                ]
            )
            live_validation._validate_args(parser, args)
            with redirect_stdout(io.StringIO()):
                code, destination = live_validation.run(args)
            self.assertEqual(code, 0)
            self.assertEqual(destination, output)
            self.assertTrue((output / "traffic.jsonl").is_file())
            self.assertTrue((output / "summary.json").is_file())
            self.assertTrue((output / "RESULTS.md").is_file())
            self.assertTrue((output / "backups" / "eeprom-01.json").is_file())
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(summary["session_status"], "completed")
            self.assertEqual(summary["identity"]["profile_key"], "fw202-format04")
            self.assertGreater(summary["audit_span"]["event_count"], 0)
            traffic = [
                json.loads(line)
                for line in (output / "traffic.jsonl").read_text().splitlines()
            ]
            transmitted = [
                event["data_ascii"]
                for event in traffic
                if event.get("event") == "traffic" and event.get("direction") == "tx"
            ]
            self.assertTrue(transmitted)
            self.assertTrue(all(value[1] == "R" for value in transmitted))
            forbidden = ("CW", "AW", "DW", "EA", "E3", "ED")
            self.assertFalse(
                any(value.startswith(forbidden) for value in transmitted)
            )

    def test_control_phase_refusal_transmits_nothing(self):
        class RefusingConsole:
            @staticmethod
            def phrase(prompt, required):
                return False

        audit = live_validation.AuditTrail(session_id="refuse-control")
        with live_validation.ControllerSession.simulated(
            "fw202-format04", allow_writes=True, audit=audit
        ) as session:
            before = len(session.client.transport.transport.controller.requests)
            with redirect_stdout(io.StringIO()):
                results = live_validation._run_control_tests(
                    session,
                    audit,
                    RefusingConsole(),
                    include_start=True,
                    start_observe_seconds=0,
                )
            after = len(session.client.transport.transport.controller.requests)
        self.assertEqual(before, after)
        self.assertEqual(results[0]["status"], "skipped")

    def test_cold_control_phase_without_start_transmits_nothing(self):
        class AcceptingConsole:
            @staticmethod
            def phrase(prompt, required):
                return True

            @staticmethod
            def confirm(statement):
                return True

        audit = live_validation.AuditTrail(session_id="cold-control")
        with live_validation.ControllerSession.simulated(
            "fw202-format04", allow_writes=True, audit=audit
        ) as session:
            controller = session.client.transport.transport.controller
            before = len(controller.requests)
            with redirect_stdout(io.StringIO()):
                results = live_validation._run_control_tests(
                    session,
                    audit,
                    AcceptingConsole(),
                    include_start=False,
                    start_observe_seconds=0,
                )
            after = len(controller.requests)
        self.assertEqual(before, after)
        self.assertEqual([item["status"] for item in results], ["skipped"] * 4)

    def test_remote_observation_survives_snapshot_timeout(self):
        class ObservingConsole:
            @staticmethod
            def phrase(prompt, required):
                return True

            @staticmethod
            def observation(prompt):
                return "yes"

        class FakeClient:
            @staticmethod
            def remote_button(button):
                return type("Receipt", (), {"request": b"CW0E14"})()

        class FakeSession:
            client = FakeClient()

            @staticmethod
            def poll_snapshot(*, request_delay):
                raise TimeoutError("snapshot unavailable")

        audit = live_validation.AuditTrail(session_id="snapshot-timeout")
        with patch.object(live_validation, "_drain_pending_frames", return_value=7):
            with redirect_stdout(io.StringIO()):
                result = live_validation._send_remote_button(
                    FakeSession(),
                    audit,
                    ObservingConsole(),
                    live_validation.RemoteButton.UP,
                    key="remote-up",
                    title="Remote UP",
                    observation_prompt="Did it move?",
                )
        self.assertEqual(result["status"], "pass")
        observations = result["observations"]
        self.assertEqual(observations["operator_observed_expected_effect"], "yes")
        self.assertIsNone(observations["after"])
        self.assertEqual(
            observations["post_command_snapshot_error"], "snapshot unavailable"
        )

    def test_off_recovery_retries_until_state_is_verified(self):
        class FakeClient:
            def __init__(self):
                self.requests = []

            def remote_button(self, button):
                self.requests.append(button)
                return SimpleNamespace(request=b"CW0E11")

        class FakeSnapshot:
            fresh = True

            def __init__(self, phase):
                self.operating_state = SimpleNamespace(phase=phase)

            def to_dict(self):
                return {"operating_state": {"phase": self.operating_state.phase}}

        class FakeSession:
            def __init__(self):
                self.client = FakeClient()
                self.polls = 0
                self.identity = SimpleNamespace(data_format=0x04)
                self.monitor = SimpleNamespace(
                    telemetry_observed_monotonic_ns=lambda index: self.state_sample_ns
                )
                self.state_sample_ns = None

            def poll_snapshot(self, *, request_delay):
                self.polls += 1
                if self.polls == 1:
                    raise TimeoutError("firmware temporarily deaf")
                if self.polls == 2:
                    self.state_sample_ns = live_validation.time.monotonic_ns()
                    return FakeSnapshot("prefill")
                self.state_sample_ns = live_validation.time.monotonic_ns()
                return FakeSnapshot("off")

        session = FakeSession()
        result = live_validation._recover_remote_off(
            session,
            timeout_seconds=1.0,
            retry_interval=0,
        )
        self.assertTrue(result["verified"])
        self.assertEqual(result["safe_state_phase"], "off")
        self.assertEqual(result["attempts"], 4)
        self.assertEqual(result["requests_hex"], ["43 57 30 45 31 31"] * 4)
        self.assertIn("temporarily deaf", result["errors"][0])
        self.assertEqual(result["state_telemetry_index"], "T0C")
        self.assertEqual(len(result["fresh_state_samples"]), 3)

    def test_off_recovery_rejects_retained_precommand_off_state(self):
        class FakeClient:
            def remote_button(self, button):
                return SimpleNamespace(request=b"CW0E11")

        class FakeSnapshot:
            fresh = True
            operating_state = SimpleNamespace(phase="off")

            @staticmethod
            def to_dict():
                return {"operating_state": {"phase": "off"}}

        class FakeSession:
            def __init__(self):
                self.client = FakeClient()
                self.identity = SimpleNamespace(data_format=0x04)
                self.polls = 0
                self.state_sample_ns = 1
                self.monitor = SimpleNamespace(
                    telemetry_observed_monotonic_ns=lambda index: self.state_sample_ns
                )

            def poll_snapshot(self, *, request_delay):
                self.polls += 1
                if self.polls > 1:
                    self.state_sample_ns = live_validation.time.monotonic_ns()
                return FakeSnapshot()

        result = live_validation._recover_remote_off(
            FakeSession(),
            timeout_seconds=1.0,
            retry_interval=0,
            required_fresh_state_samples=1,
        )
        self.assertTrue(result["verified"])
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(result["fresh_state_samples"]), 1)

    def test_nonempty_destination_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            (destination / "existing.txt").write_text("preserve me")
            with self.assertRaises(FileExistsError):
                live_validation._prepare_output_directory(destination)


if __name__ == "__main__":
    unittest.main()
