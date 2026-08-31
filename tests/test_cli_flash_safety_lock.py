import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openmaxfire.cli import main


ROOT = Path(__file__).resolve().parents[1]
FW206 = (
    ROOT
    / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex"
)


class CliFlashSafetyLockTests(unittest.TestCase):
    def test_live_programming_is_rejected_before_any_access_or_prompt(self):
        error = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "must-not-exist"
            with mock.patch(
                "openmaxfire.cli.FirmwareImage.load", side_effect=AssertionError
            ):
                with mock.patch(
                    "openmaxfire.cli.SerialTransport", side_effect=AssertionError
                ):
                    with mock.patch("builtins.input", side_effect=AssertionError):
                        with contextlib.redirect_stderr(error):
                            result = main(
                                [
                                    "--port",
                                    "SIM0",
                                    "--baud",
                                    "9600",
                                    "flash",
                                    "not-opened.hex",
                                    "--session-dir",
                                    str(session),
                                ]
                            )

            self.assertEqual(result, 4)
            self.assertFalse(session.exists())
        self.assertIn("Refusing physical loader traffic", error.getvalue())
        self.assertIn("manual AC/BREAK", error.getvalue())

    def test_live_recovery_is_rejected_before_bundle_serial_or_session_access(self):
        error = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = root / "must-not-exist"
            source = root / "not-opened"
            with mock.patch(
                "openmaxfire.cli.load_recovery_bundle", side_effect=AssertionError
            ):
                with mock.patch(
                    "openmaxfire.cli.SerialTransport", side_effect=AssertionError
                ):
                    with mock.patch("builtins.input", side_effect=AssertionError):
                        with contextlib.redirect_stderr(error):
                            result = main(
                                [
                                    "--port",
                                    "SIM0",
                                    "--baud",
                                    "9600",
                                    "flash",
                                    "--session-dir",
                                    str(session),
                                    "--recover-from-session",
                                    str(source),
                                ]
                            )

            self.assertEqual(result, 4)
            self.assertFalse(session.exists())
        self.assertIn("Refusing physical loader traffic", error.getvalue())

    def test_plan_only_remains_reachable_without_serial_access(self):
        image = object()
        with mock.patch("openmaxfire.cli.FirmwareImage.load", return_value=image):
            with mock.patch("openmaxfire.cli.approve_live_firmware"):
                with mock.patch(
                    "openmaxfire.cli._run_flash_plan", return_value=0
                ) as run_plan:
                    with mock.patch(
                        "openmaxfire.cli.SerialTransport", side_effect=AssertionError
                    ):
                        result = main(
                            [
                                "flash",
                                "authenticated.hex",
                                "--plan-only",
                                "--current-profile",
                                "fw202-format04",
                            ]
                        )

        self.assertEqual(result, 0)
        run_plan.assert_called_once()

    def test_rehearsal_is_rejected_before_image_serial_session_or_prompt(self):
        error = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "must-not-exist"
            with mock.patch("openmaxfire.cli.FirmwareImage.load", side_effect=AssertionError):
                with mock.patch(
                    "openmaxfire.cli.SerialTransport", side_effect=AssertionError
                ):
                    with mock.patch("builtins.input", side_effect=AssertionError):
                        with contextlib.redirect_stderr(error):
                            result = main(
                                [
                                    "--port", "SIM0",
                                    "--baud", "9600",
                                    "flash", "not-opened.hex",
                                    "--session-dir", str(session),
                                    "--rehearsal-only",
                                    "--hold-tx-break-during-power-off",
                                ]
                            )

            self.assertEqual(result, 4)
            self.assertFalse(session.exists())
        self.assertIn("Refusing physical loader traffic", error.getvalue())
        self.assertIn("Only flash --plan-only", error.getvalue())

    def test_help_states_that_all_physical_loader_traffic_is_disabled(self):
        output = io.StringIO()
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(output):
                main(["flash", "--help"])

        self.assertEqual(raised.exception.code, 0)
        help_text = output.getvalue()
        self.assertIn("All physical loader traffic", help_text)
        self.assertIn("including non-writing rehearsal", help_text)
        self.assertIn("retired; physical EA/EB and ED/E4 traffic", help_text)
        self.assertIn("--confirm-actuator-loads-unplugged", help_text)


if __name__ == "__main__":
    unittest.main()
