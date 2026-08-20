import unittest

from openmaxfire.protocol import (
    RemoteButton,
    encode_read_register,
    encode_remote_button,
    encode_write_register,
)


class ProtocolEncodingTests(unittest.TestCase):
    def test_read_register_encoding(self):
        self.assertEqual(encode_read_register(0x00), b"CR00")
        self.assertEqual(encode_read_register(0x0E), b"CR0E")
        self.assertEqual(encode_read_register(0xFF), b"CRFF")

    def test_write_register_encoding(self):
        self.assertEqual(encode_write_register(0x0E, 0x14), b"CW0E14")
        self.assertEqual(encode_write_register(0xFF, 0x00), b"CWFF00")

    def test_remote_button_encodings_reconstructed_from_bixcheck_5501(self):
        self.assertEqual(encode_remote_button(RemoteButton.OFF), b"CW0E11")
        self.assertEqual(encode_remote_button(RemoteButton.ON), b"CW0E12")
        self.assertEqual(encode_remote_button(RemoteButton.UP), b"CW0E14")
        self.assertEqual(encode_remote_button(RemoteButton.DOWN), b"CW0E18")


if __name__ == "__main__":
    unittest.main()
