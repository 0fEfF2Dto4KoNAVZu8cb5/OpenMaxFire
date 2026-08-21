import contextlib
import io
import unittest
from unittest import mock

from openmaxfire.cli import main
from openmaxfire.client import StoveIdentity
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


if __name__ == "__main__":
    unittest.main()
