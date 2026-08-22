import unittest

from openmaxfire.client import MaxFireClient


class FakeTransport:
    def __init__(self, incoming: bytes = b""):
        self.incoming = bytearray(incoming)
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, data: bytes) -> None:
        self.writes.append(data)

    def read(self, size: int = 1) -> bytes:
        if not self.incoming:
            return b""
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk

    def close(self) -> None:
        self.closed = True


class ClientReadOnlyTests(unittest.TestCase):
    def test_query_register_skips_interleaved_telemetry(self):
        transport = FakeTransport(b"T0913\nCR0807\n")
        response = MaxFireClient(transport).query_register(0x08)
        self.assertEqual(response.value, 0x07)
        self.assertEqual(transport.writes, [b"CR08"])

    def test_query_register_has_no_default_frame_limit(self):
        telemetry = b"".join(f"T{index:02x}00\n".encode() for index in range(32))
        transport = FakeTransport(telemetry + b"CR0807\n")
        response = MaxFireClient(transport).query_register(0x08)
        self.assertEqual(response.value, 0x07)
        self.assertEqual(transport.writes, [b"CR08"])

    def test_query_register_reports_transport_timeout(self):
        transport = FakeTransport(b"T0000\nT0100\n")
        with self.assertRaisesRegex(
            TimeoutError,
            r"no matching CR08 response before serial timeout after 2 frame\(s\)",
        ):
            MaxFireClient(transport).query_register(0x08)

    def test_query_register_resynchronizes_after_partial_opening_line(self):
        transport = FakeTransport(b"0f\nT0000\nCR0b02\n")
        response = MaxFireClient(transport).query_register(0x0B)
        self.assertEqual(response.value, 0x02)
        self.assertEqual(transport.writes, [b"CR0B"])

    def test_identify_uses_safe_order_and_recognizes_271(self):
        transport = FakeTransport(
            b"CR0000\nCR0807\nCR0b02\nCR0c71\nCR0d00\nCR0e00\n"
        )
        identity = MaxFireClient(transport).identify()
        self.assertEqual(identity.firmware_version, "2.71")
        self.assertTrue(identity.recognized)
        self.assertEqual(
            transport.writes,
            [b"CR00", b"CR08", b"CR0B", b"CR0C", b"CR0D", b"CR0E"],
        )

    def test_identify_recognizes_live_202_format04_pairing(self):
        transport = FakeTransport(
            b"CR0000\nCR0804\nCR0b02\nCR0c02\nCR0d00\nCR0e00\n"
        )
        identity = MaxFireClient(transport).identify()
        self.assertEqual(identity.firmware_version, "2.02")
        self.assertEqual(identity.data_format, 0x04)
        self.assertTrue(identity.recognized)

    def test_read_eeprom_uses_a_space_only(self):
        transport = FakeTransport(b"AR00AA\nAR01BB\nAR0207\n")
        values = MaxFireClient(transport).read_eeprom(first=0, last=2)
        self.assertEqual(values, {0: 0xAA, 1: 0xBB, 2: 0x07})
        self.assertEqual(transport.writes, [b"AR00", b"AR01", b"AR02"])

    def test_mismatched_address_is_bounded(self):
        transport = FakeTransport(b"CR0100\nCR0200\n")
        with self.assertRaises(TimeoutError):
            MaxFireClient(transport).query_register(0x08, max_frames=2)

    def test_invalid_explicit_frame_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            MaxFireClient(FakeTransport()).query_register(0x08, max_frames=0)


if __name__ == "__main__":
    unittest.main()
