import contextlib
import io
import unittest

from openmaxfire.cli import main


class CliTests(unittest.TestCase):
    def test_offline_encode_does_not_require_serial_settings(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["encode", "button", "up"])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "CW0E14")

    def test_live_read_requires_port_and_baud(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(["read", "0x00"])
        self.assertEqual(result, 2)
        self.assertIn("--port and --baud", error.getvalue())

    def test_live_read_requires_explicit_unverified_io_ack(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(["--port", "/dev/null", "--baud", "38400", "read", "0x00"])
        self.assertEqual(result, 3)
        self.assertIn("Refusing live I/O", error.getvalue())


if __name__ == "__main__":
    unittest.main()
