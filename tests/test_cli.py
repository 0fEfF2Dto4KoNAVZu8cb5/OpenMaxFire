import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openmaxfire.cli import main
from openmaxfire.client import CommandReceipt, StoveIdentity
from openmaxfire.protocol import AddressedResponse, TelemetryResponse
from openmaxfire.transport import SerialPortInfo


class CliTests(unittest.TestCase):
    def test_offline_encode_does_not_require_serial_settings(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["encode", "button", "up"])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "CW0E14")

    def test_offline_encode_supports_generic_unit(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["encode", "read", "0x03", "--unit", "A"])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "AR03")

    def test_ports_lists_cross_platform_metadata_without_live_ack(self):
        output = io.StringIO()
        fixture = [
            SerialPortInfo(
                "COM7",
                "USB Serial",
                vid=0x0403,
                pid=0x6001,
                serial_number="ABC",
                manufacturer="FTDI",
            )
        ]
        with mock.patch("openmaxfire.cli.list_serial_ports", return_value=fixture):
            with contextlib.redirect_stdout(output):
                result = main(["ports"])
        self.assertEqual(result, 0)
        self.assertIn("COM7", output.getvalue())
        self.assertIn("0403:6001", output.getvalue())

    def test_live_read_requires_port_and_baud(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(["read", "0x00"])
        self.assertEqual(result, 2)
        self.assertIn("--port and --baud", error.getvalue())

    def test_live_read_requires_explicit_unverified_io_ack(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(["--port", "/dev/null", "--baud", "9600", "read", "0x00"])
        self.assertEqual(result, 3)
        self.assertIn("Refusing live I/O", error.getvalue())

    def test_live_write_requires_separate_state_change_ack(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(
                [
                    "--port", "COM7",
                    "--baud", "9600",
                    "write", "0x01", "0x02",
                    "--i-understand-unverified-io",
                ]
            )
        self.assertEqual(result, 3)
        self.assertIn("Refusing state-changing traffic", error.getvalue())

    def test_live_generic_write_can_verify_d_space(self):
        class FakeClient:
            closed = False

            def write_register_verified(self, address, value, *, unit, settle_delay):
                self.call = (address, value, unit, settle_delay)
                return CommandReceipt(b"DW1234", b"DR1234", True)

            def close(self):
                self.closed = True

        client = FakeClient()
        output = io.StringIO()
        with mock.patch("openmaxfire.cli._connect", return_value=client):
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "--port", "COM7",
                        "--baud", "9600",
                        "write", "0x12", "0x34",
                        "--unit", "D",
                        "--verify",
                        "--settle-delay", "0",
                        "--i-understand-unverified-io",
                        "--i-understand-this-can-change-stove-state",
                    ]
                )
        self.assertEqual(result, 0)
        self.assertEqual(client.call, (0x12, 0x34, "D", 0.0))
        self.assertIn("verified=yes", output.getvalue())
        self.assertTrue(client.closed)

    def test_raw_exchange_preserves_exact_bytes_and_marks_unverified(self):
        class FakeClient:
            closed = False

            def exchange_raw(self, payload, *, receive_duration):
                self.call = (payload, receive_duration)
                return CommandReceipt(payload, b"CR0000\n", False)

            def close(self):
                self.closed = True

        client = FakeClient()
        output = io.StringIO()
        with mock.patch("openmaxfire.cli._connect", return_value=client):
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "--port", "COM7",
                        "--baud", "9600",
                        "raw", "--hex", "43 52 30 30",
                        "--read-for", "0.25",
                        "--json",
                        "--i-understand-unverified-io",
                        "--i-understand-this-can-change-stove-state",
                    ]
                )
        self.assertEqual(result, 0)
        self.assertEqual(client.call, (b"CR00", 0.25))
        document = json.loads(output.getvalue())
        self.assertEqual(document["rx_hex"], "43 52 30 30 30 30 0A")
        self.assertFalse(document["verified"])
        self.assertTrue(client.closed)

    def test_raw_mode_rejects_known_loader_entry_before_opening_port(self):
        error = io.StringIO()
        with mock.patch("openmaxfire.cli._connect", side_effect=AssertionError):
            with contextlib.redirect_stderr(error):
                result = main(
                    [
                        "--port", "COM7",
                        "--baud", "9600",
                        "raw", "--ascii", "CW0FC4",
                        "--i-understand-unverified-io",
                        "--i-understand-this-can-change-stove-state",
                    ]
                )
        self.assertEqual(result, 4)
        self.assertIn("firmware-loader traffic is isolated", error.getvalue())

    def test_transaction_dry_run_does_not_open_serial_port(self):
        plan = {
            "schema": "openmaxfire.transaction.v1",
            "description": "read-only check",
            "operations": [{"op": "read", "unit": "D", "address": "0x12"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            output = io.StringIO()
            with mock.patch("openmaxfire.cli._connect", side_effect=AssertionError):
                with contextlib.redirect_stdout(output):
                    result = main(["transaction", str(path), "--dry-run", "--json"])
        self.assertEqual(result, 0)
        canonical = json.loads(output.getvalue())
        self.assertEqual(canonical["operations"][0]["address"], "0x12")

    def test_identify_outputs_recognized_version(self):
        class FakeClient:
            closed = False

            def identify(self, *, request_delay):
                self.request_delay = request_delay
                return StoveIdentity(0, 7, 2, 0x71, 0, 0)

            def close(self):
                self.closed = True

        client = FakeClient()
        output = io.StringIO()
        with mock.patch("openmaxfire.cli._connect", return_value=client):
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "--port",
                        "COM7",
                        "--baud",
                        "19200",
                        "identify",
                        "--i-understand-unverified-io",
                    ]
                )
        self.assertEqual(result, 0)
        self.assertIn("Firmware: 2.71", output.getvalue())
        self.assertTrue(client.closed)

    def test_replay_is_offline_and_emits_machine_readable_snapshot(self):
        events = [
            {"event": "session", "metadata": {"baudrate": 9600}},
            {
                "event": "traffic",
                "direction": "rx",
                "data_hex": "43 52 30 38 30 37 0A 54 30 39 32 30 0A",
                "monotonic_ns": 1,
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.jsonl"
            path.write_text("".join(json.dumps(item) + "\n" for item in events))
            output = io.StringIO()
            with mock.patch("openmaxfire.cli._connect", side_effect=AssertionError):
                with contextlib.redirect_stdout(output):
                    result = main(["replay", str(path), "--json"])
        self.assertEqual(result, 0)
        snapshot = json.loads(output.getvalue())
        self.assertEqual(snapshot["source"], "replay")
        self.assertEqual(snapshot["decoded"]["operating_state"]["label"], "Off")

    def test_monitor_one_cycle_polls_only_controller_reads(self):
        class FakeClient:
            def __init__(self):
                self.addresses = []
                self.closed = False

            def query_register(self, address, *, on_frame):
                self.addresses.append(address)
                value = 0x07 if address == 0x08 else 0
                raw = f"CR{address:02x}{value:02x}".encode("ascii")
                response = AddressedResponse("C", "R", address, value, raw)
                on_frame(response)
                if address == 0x08:
                    on_frame(TelemetryResponse(0x09, (0x20,), b"T0920"))
                return response

            def close(self):
                self.closed = True

        client = FakeClient()
        output = io.StringIO()
        with mock.patch("openmaxfire.cli._connect", return_value=client):
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "--port", "COM7",
                        "--baud", "9600",
                        "--request-delay", "0",
                        "monitor",
                        "--cycles", "1",
                        "--json",
                        "--i-understand-unverified-io",
                    ]
                )
        self.assertEqual(result, 0)
        self.assertEqual(client.addresses, list(range(0x0F)))
        self.assertTrue(client.closed)
        snapshot = json.loads(output.getvalue())
        self.assertTrue(snapshot["poll"]["read_only"])
        self.assertEqual(snapshot["decoded"]["operating_state"]["label"], "Off")

    def test_monitor_rejects_shared_raw_and_decoded_log_path(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(
                [
                    "--port", "COM7",
                    "--baud", "9600",
                    "--traffic-log", "same.jsonl",
                    "monitor",
                    "--cycles", "1",
                    "--output", "same.jsonl",
                    "--i-understand-unverified-io",
                ]
            )
        self.assertEqual(result, 2)
        self.assertIn("must be different files", error.getvalue())


if __name__ == "__main__":
    unittest.main()
