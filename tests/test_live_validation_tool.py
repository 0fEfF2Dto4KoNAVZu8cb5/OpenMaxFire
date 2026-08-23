import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


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

    def test_nonempty_destination_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            (destination / "existing.txt").write_text("preserve me")
            with self.assertRaises(FileExistsError):
                live_validation._prepare_output_directory(destination)


if __name__ == "__main__":
    unittest.main()
