import unittest

from openmaxfire.protocol import (
    AddressedResponse,
    ProtocolError,
    RemoteButton,
    ResponseLineParser,
    StatusResponse,
    TelemetryResponse,
    combine_telemetry_word,
    calculate_configuration_checksum,
    decode_igniter_state,
    decode_operating_state,
    decode_register_request,
    encode_read_register,
    encode_remote_button,
    encode_write_register,
    parse_response_line,
    percentage_to_stove_multiply_parameter,
    stove_multiply_parameter_to_percentage,
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

    def test_generic_units_and_request_decoder(self):
        self.assertEqual(encode_read_register(0x02, unit="A"), b"AR02")
        self.assertEqual(encode_write_register(0x9B, 0x40, unit="D"), b"DW9B40")
        self.assertEqual(
            decode_register_request(b"CR0E"),
            decode_register_request(memoryview(b"CR0E")),
        )
        request = decode_register_request(b"AW6B40")
        self.assertEqual((request.unit, request.opcode, request.address, request.value),
                         ("A", "W", 0x6B, 0x40))

    def test_request_decoder_rejects_terminators_and_lowercase_hex(self):
        with self.assertRaises(ProtocolError):
            decode_register_request(b"CR0E\n")
        with self.assertRaises(ProtocolError):
            decode_register_request(b"CR0e")


class ProtocolResponseTests(unittest.TestCase):
    def test_addressed_response(self):
        frame = parse_response_line(b"\x01CR0e14\r\n")
        self.assertIsInstance(frame, AddressedResponse)
        self.assertEqual((frame.unit, frame.opcode, frame.address, frame.value),
                         ("C", "R", 0x0E, 0x14))

    def test_leading_nul_resynchronizes_first_fw206_reply(self):
        frame = parse_response_line(b"\x00CR0000\n")
        self.assertIsInstance(frame, AddressedResponse)
        self.assertEqual((frame.unit, frame.opcode, frame.address, frame.value),
                         ("C", "R", 0x00, 0x00))

    def test_embedded_nul_remains_invalid(self):
        with self.assertRaises(ProtocolError):
            parse_response_line(b"CR00\x0000\n")

    def test_single_and_double_byte_telemetry(self):
        single = parse_response_line(b"T19af\n")
        double = parse_response_line(b"T0A1234\r")
        self.assertEqual(single, TelemetryResponse(0x19, (0xAF,), b"T19af"))
        self.assertEqual(double, TelemetryResponse(0x0A, (0x12, 0x34), b"T0A1234"))

    def test_status_response_is_preserved_without_inventing_semantics(self):
        self.assertEqual(
            parse_response_line(b"IREADY\n"),
            StatusResponse(kind="I", payload=b"READY", raw=b"IREADY"),
        )

    def test_incremental_cr_lf_splitter(self):
        parser = ResponseLineParser()
        self.assertEqual(parser.feed(b"T"), [])
        frames = parser.feed(b"19AF\r\nCR0807\n")
        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].values, (0xAF,))
        self.assertEqual(frames[1].value, 0x07)
        self.assertEqual(parser.pending, b"")

    def test_strict_lengths(self):
        for invalid in (b"CR00", b"CR000000", b"T00", b"T00000000", b"X00"):
            with self.subTest(invalid=invalid), self.assertRaises(ProtocolError):
                parse_response_line(invalid)

    def test_firmware_telemetry_words_are_big_endian_adjacent_slots(self):
        self.assertEqual(combine_telemetry_word(0x12, 0x34), 0x1234)
        with self.assertRaises(ValueError):
            combine_telemetry_word(0x100, 0)

    def test_bixcheck_t09_state_labels(self):
        expected = {
            0x10: ("Cooldown", None, False),
            0x20: ("Off", None, False),
            0x30: ("Prefill", None, False),
            0x31: ("Started", None, False),
            0x32: ("Starting", None, False),
            0x33: ("Ignited", None, False),
            0x37: ("Error", None, False),
            0x40: ("Level 1", 1, False),
            0x4B: ("TSTAT L 4", 4, True),
            0x56: ("Ramping", 7, False),
            0x60: ("Ash dump", None, False),
            0x70: ("Undefined: 70", None, False),
            0xC3: ("Level 4", 4, False),
        }
        for raw, values in expected.items():
            with self.subTest(raw=raw):
                state = decode_operating_state(raw)
                self.assertEqual(
                    (state.label, state.level, state.thermostat), values
                )

    def test_bixcheck_t08_igniter_labels_ignore_high_bits(self):
        expected = {
            0x00: "L R failed",
            0x01: "R failed",
            0x02: "L failed",
            0x03: "Error",
            0x06: "Error",
            0x07: "L R good",
            0x87: "L R good",
        }
        for raw, label in expected.items():
            with self.subTest(raw=raw):
                state = decode_igniter_state(raw)
                self.assertEqual((state.code, state.label), (raw & 0x07, label))


class BixCheckMathTests(unittest.TestCase):
    def test_lean_burn_display_conversions(self):
        self.assertEqual(stove_multiply_parameter_to_percentage(0, 0x6B), 0)
        self.assertEqual(stove_multiply_parameter_to_percentage(64, 0x6B), 50)
        self.assertEqual(stove_multiply_parameter_to_percentage(127, 0x9B), 100)
        self.assertEqual(stove_multiply_parameter_to_percentage(167, 0x6C), 30)
        self.assertEqual(stove_multiply_parameter_to_percentage(89, 0x6C), -30)
        self.assertEqual(stove_multiply_parameter_to_percentage(89, 0x6D), 30)
        self.assertEqual(stove_multiply_parameter_to_percentage(167, 0x6D), -30)

    def test_lean_burn_inverse_uses_bixcheck_rounding(self):
        self.assertEqual(percentage_to_stove_multiply_parameter(50, 0x6B), 64)
        self.assertEqual(percentage_to_stove_multiply_parameter(100, 0x9B), 128)
        self.assertEqual(percentage_to_stove_multiply_parameter(30, 0x6C), 167)
        self.assertEqual(percentage_to_stove_multiply_parameter(-30, 0x6C), 89)
        self.assertEqual(percentage_to_stove_multiply_parameter(30, 0x6D), 89)
        self.assertEqual(percentage_to_stove_multiply_parameter(-30, 0x6D), 167)

    def test_configuration_checksum_add_then_rotate(self):
        eeprom = {address: 0 for address in range(0x02, 0x4C)}
        eeprom[0x02] = 1
        self.assertEqual(calculate_configuration_checksum(0, eeprom), 0x0400)

    def test_configuration_checksum_requires_complete_confirmed_range(self):
        with self.assertRaises(ValueError):
            calculate_configuration_checksum(6, b"\0" * 256)
        with self.assertRaises(ValueError):
            calculate_configuration_checksum(7, {0x02: 0})


if __name__ == "__main__":
    unittest.main()
