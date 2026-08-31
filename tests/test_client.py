import unittest

from openmaxfire.client import MaxFireClient
from openmaxfire.errors import SafetyInterlockError


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

    def test_query_register_does_not_mistake_write_echo_for_readback(self):
        transport = FakeTransport(b"CW0811\nCR0807\n")
        response = MaxFireClient(transport).query_register(0x08)
        self.assertEqual(response.value, 0x07)
        self.assertEqual(transport.writes, [b"CR08"])

    def test_query_register_reports_every_valid_frame_to_monitor_callback(self):
        transport = FakeTransport(b"T094b\nCR0804\n")
        observed = []
        response = MaxFireClient(transport).query_register(0x08, on_frame=observed.append)
        self.assertEqual(response.value, 0x04)
        self.assertEqual([type(frame).__name__ for frame in observed],
                         ["TelemetryResponse", "AddressedResponse"])

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

    def test_read_only_retry_reissues_request_after_telemetry_timeout(self):
        class RetryTransport(FakeTransport):
            def write(self, data: bytes) -> None:
                super().write(data)
                if len(self.writes) == 2:
                    self.incoming.extend(b"CR0804\n")

        transport = RetryTransport(b"T0000\nT0100\n")
        identity_client = MaxFireClient(transport)
        response = identity_client._query_read_only_with_retries(
            0x08,
            attempts=2,
        )
        self.assertEqual(response.value, 0x04)
        self.assertEqual(transport.writes, [b"CR08", b"CR08"])

    def test_read_only_retry_count_is_bounded(self):
        client = MaxFireClient(FakeTransport())
        with self.assertRaises(ValueError):
            client._query_read_only_with_retries(0x08, attempts=0)
        with self.assertRaises(ValueError):
            client._query_read_only_with_retries(0x08, attempts=6)

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

    def test_generic_write_can_target_all_addressed_units(self):
        transport = FakeTransport()
        receipt = MaxFireClient(transport).write_register(0x6B, 0x40, unit="A")
        self.assertEqual(receipt.request, b"AW6B40")
        self.assertFalse(receipt.verified)
        self.assertEqual(transport.writes, [b"AW6B40"])

    def test_send_only_read_can_target_d_space(self):
        transport = FakeTransport()
        receipt = MaxFireClient(transport).read_register(0x12, unit="D")
        self.assertEqual(receipt.request, b"DR12")
        self.assertEqual(transport.writes, [b"DR12"])

    def test_verified_write_uses_fresh_read_response(self):
        transport = FakeTransport(b"AW6B40\nAR6b40\n")
        receipt = MaxFireClient(transport).write_register_verified(
            0x6B, 0x40, unit="A"
        )
        self.assertEqual(transport.writes, [b"AW6B40", b"AR6B"])
        self.assertEqual(receipt.response, b"AR6b40")
        self.assertTrue(receipt.verified)

    def test_verified_write_reports_mismatched_readback(self):
        transport = FakeTransport(b"AR6b41\n")
        receipt = MaxFireClient(transport).write_register_verified(
            0x6B, 0x40, unit="A"
        )
        self.assertFalse(receipt.verified)

    def test_invalid_raw_receive_duration_sends_nothing(self):
        transport = FakeTransport()
        with self.assertRaises(ValueError):
            MaxFireClient(transport).exchange_raw(b"CR00", receive_duration=-1)
        self.assertEqual(transport.writes, [])

    def test_generic_client_rejects_binary_loader_markers_anywhere(self):
        for payload in (b"\xEA", b"prefix\xE3payload", b"\xED", b"x\xE7y"):
            with self.subTest(payload=payload):
                transport = FakeTransport()
                with self.assertRaises(SafetyInterlockError):
                    MaxFireClient(transport).send_raw(payload)
                self.assertEqual(transport.writes, [])

    def test_generic_client_blocks_split_cw0fc4_before_final_bytes(self):
        transport = FakeTransport()
        client = MaxFireClient(transport)
        with self.assertRaises(SafetyInterlockError):
            client.send_raw(b"CW0F")
        self.assertEqual(transport.writes, [])

    def test_generic_raw_rejects_fragmented_or_arbitrary_byte_streams(self):
        for payload in (b"C", b"W0F", b"C4", b"hello", b"\x01\x02\x03\x04"):
            with self.subTest(payload=payload):
                transport = FakeTransport()
                with self.assertRaises(SafetyInterlockError):
                    MaxFireClient(transport).send_raw(payload)
                self.assertEqual(transport.writes, [])

    def test_split_cw0fc4_guard_is_shared_by_clients_on_one_transport(self):
        transport = FakeTransport()
        with self.assertRaises(SafetyInterlockError):
            MaxFireClient(transport).send_raw(b"CW0F")
        with self.assertRaises(SafetyInterlockError):
            MaxFireClient(transport).send_raw(b"FC4")
        self.assertEqual(transport.writes, [])

    def test_raw_stream_stays_locked_after_indeterminate_write_error(self):
        class FailingTransport(FakeTransport):
            def write(self, data):
                self.writes.append(bytes(data))
                raise OSError("flush failed after possible transmission")

        transport = FailingTransport()
        client = MaxFireClient(transport)
        with self.assertRaises(OSError):
            client.send_raw(b"CR00")
        with self.assertRaises(SafetyInterlockError):
            client.send_raw(b"CR01")
        self.assertEqual(transport.writes, [b"CR00"])

    def test_generic_c_write_cannot_enter_loader(self):
        transport = FakeTransport()
        with self.assertRaises(SafetyInterlockError):
            MaxFireClient(transport).write_register(0x0F, 0xC4, unit="C")
        self.assertEqual(transport.writes, [])


if __name__ == "__main__":
    unittest.main()
