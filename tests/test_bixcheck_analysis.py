import struct
import unittest
from pathlib import Path

from tools.analyze_bixcheck import (
    CHECKOUT_RECORD_SIZE,
    PEImage,
    RECORD_SIZE,
    decode_checkout_record,
    decode_data_element,
    normalize_instruction,
    parse_disassembly,
    parse_symbols,
)
from tools.virtual_serial_lab import RequestStreamParser, VirtualStove
from openmaxfire.protocol import ProtocolError
from tools.firmware_pipeline import CR_HANDLER_MATRIX, parse_ihex
from tools.pic14_emulator import (
    PIC16F877A,
    RESPONSE_FORMATTERS,
    SFR_ADCON0,
    SFR_ADCON1,
    SFR_ADRESH,
    SFR_ADRESL,
    SFR_PORTD,
    SFR_PORTE,
    SFR_TRISD,
    calculate_fixture_checksum,
    execute_request,
    probe_image,
    synthetic_controller_eeprom,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AnalyzerParserTests(unittest.TestCase):
    def test_pe_metadata_for_preserved_5501(self):
        image = PEImage(
            REPO_ROOT / "preservation" / "original" / "binaries" / "BixCheck_080315.exe"
        )
        self.assertEqual(image.machine, 0x014C)
        self.assertEqual(image.timestamp, 1205641881)
        self.assertEqual(image.section(".data").virtual_address, 0x39000)

    def test_coff_source_and_function_symbol_parser(self):
        text = """
[ 25](sec -2)(fl 0x00)(ty 0)(scl 103) (nx 1) 0x2f async.cpp
[ 27](sec  1)(fl 0x00)(ty 20)(scl   2) (nx 1) 0x2e0 async::set_timeout(long)
"""
        symbols = parse_symbols(text)
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].source, "async.cpp")
        self.assertEqual(symbols[0].offset, 0x2E0)

    def test_disassembly_and_normalization_remove_build_addresses(self):
        parsed = parse_disassembly(
            "  407990:\t74 15                \tje 4079a7 <thing(int)+0x37>\n"
            "  407992:\ta1 00 90 43 00       \tmov eax,ds:0x439000\n"
        )
        self.assertEqual(len(parsed), 2)
        self.assertEqual(normalize_instruction(parsed[0x407990].assembly, "thing(int)"),
                         "je <LOCAL>")
        self.assertIn("ADDR", normalize_instruction(parsed[0x407992].assembly, "thing(int)"))

    def test_data_element_layout(self):
        record = bytearray(RECORD_SIZE)
        record[0] = 2
        record[1:5] = b"Test"
        record[0x21:0x25] = b"unit"
        struct.pack_into("<i", record, 0x44, -4)
        record[0x48:0x4A] = b"A\x6c"
        struct.pack_into("<i", record, 0x4C, 30)
        struct.pack_into("<i", record, 0x50, -30)
        struct.pack_into("<H", record, 0x54, 1)
        struct.pack_into("<H", record, 0x56, 2)
        decoded = decode_data_element(bytes(record))
        self.assertEqual(decoded["label"], "Test")
        self.assertEqual(decoded["value_or_default"], -4)
        self.assertEqual(decoded["address_hex"], "0x6C")

    def test_checkout_layout(self):
        record = bytearray(CHECKOUT_RECORD_SIZE)
        record[0] = 1
        record[1:6] = b"Plate"
        record[0x21:0x28] = b"Testing"
        record[0xA1:0xA6] = b"Motor"
        decoded = decode_checkout_record(bytes(record))
        self.assertEqual((decoded["label"], decoded["instruction"], decoded["failure_hint"]),
                         ("Plate", "Testing", "Motor"))


class VirtualSerialLabTests(unittest.TestCase):
    def test_unterminated_stream_chunking(self):
        parser = RequestStreamParser()
        self.assertEqual(parser.feed(b"CR"), [])
        requests = parser.feed(b"08AW6B40CR0B")
        self.assertEqual([(item.unit, item.opcode, item.address, item.value) for item in requests],
                         [("C", "R", 0x08, None), ("A", "W", 0x6B, 0x40),
                          ("C", "R", 0x0B, None)])

    def test_virtual_stove_is_read_only_by_default(self):
        parser = RequestStreamParser()
        stove = VirtualStove()
        read, write = parser.feed(b"CR08CW0E14")
        self.assertEqual(stove.transact(read), (b"CR0807\n", "synthetic read"))
        self.assertEqual(stove.transact(write), (b"IWRITE-BLOCKED\n", "write blocked"))

    def test_virtual_stove_configuration_checksum_is_valid(self):
        stove = VirtualStove()
        eeprom = {
            address: stove.registers.get(("A", address), 0)
            for address in range(0x100)
        }
        stored = (eeprom[0] << 8) | eeprom[1]
        self.assertEqual(stored, calculate_fixture_checksum(7, bytes(eeprom.values())))

    def test_lab_never_accepts_downloader_identify_byte(self):
        with self.assertRaises(ProtocolError):
            RequestStreamParser().feed(b"\xEA")


class FirmwareEmulationTests(unittest.TestCase):
    @staticmethod
    def firmware_cpu(version: str = "2.71") -> PIC16F877A:
        filenames = {
            "2.06": "2.06/extracted/Bixby_02060021_Downloader.hex",
            "2.70": "2.70/extracted/Bixby_0270_070206.hex",
            "2.71": "2.71/extracted/Bixby_0271_080315.hex",
        }
        data_format = 5 if version == "2.06" else 7
        image = parse_ihex(
            (
                REPO_ROOT
                / "reverse-engineering"
                / "firmware"
                / filenames[version]
            ).read_bytes()
        )
        return PIC16F877A(
            image, data_eeprom=synthetic_controller_eeprom(data_format)
        )

    def test_real_271_firmware_executes_cr00_path(self):
        summary, _trace, _events = probe_image(
            REPO_ROOT
            / "reverse-engineering"
            / "firmware"
            / "2.71"
            / "extracted"
            / "Bixby_0271_080315.hex",
            "test-2.71",
            b"CR00",
            "unit-test probe",
            boot_steps=10_000,
            probe_steps=100_000,
        )
        self.assertIsNone(summary["error"])
        self.assertEqual(summary["tx_hex"], "43 52 30 30 30 30 0A")
        self.assertEqual(summary["rx_bytes_remaining"], 0)

    def test_real_pickit_loader_executes_identify_path(self):
        summary, _trace, _events = probe_image(
            REPO_ROOT
            / "reverse-engineering"
            / "firmware"
            / "2.06"
            / "extracted"
            / "Bixby_02060021_PICkit.hex",
            "test-loader",
            b"\xEA",
            "unit-test probe",
            boot_steps=0,
            probe_steps=1_000,
        )
        self.assertIsNone(summary["error"])
        self.assertEqual(summary["tx_hex"], "EB")
        self.assertEqual(summary["steps_executed"], 43)

    def test_recovered_202_pickit_loader_executes_identify_path(self):
        summary, _trace, _events = probe_image(
            REPO_ROOT
            / "reverse-engineering"
            / "firmware"
            / "2.02"
            / "extracted"
            / "Bixby_0202_260827_PICkit.hex",
            "test-2.02-loader",
            b"\xEA",
            "unit-test probe",
            boot_steps=0,
            probe_steps=1_000,
        )
        self.assertIsNone(summary["error"])
        self.assertEqual(summary["tx_hex"], "EB")
        self.assertEqual(summary["steps_executed"], 43)

    def test_gpio_input_levels_are_separate_from_output_latch(self):
        cpu = self.firmware_cpu()
        cpu.ram[SFR_TRISD] = 0x01
        cpu.ram[SFR_PORTD] = 0xFE
        cpu.set_gpio_bit("PORTD", 0, True)
        self.assertEqual(cpu.read_file(SFR_PORTD), 0xFF)
        cpu.write_file(SFR_PORTD, 0x00)
        self.assertEqual(cpu.ram[SFR_PORTD], 0x00)
        self.assertEqual(cpu.read_file(SFR_PORTD), 0x01)

    def test_adc_model_samples_selected_channel_in_both_formats(self):
        cpu = self.firmware_cpu()
        cpu.set_adc_input(3, 0x2AB)
        cpu.ram[SFR_ADCON1] = 0x80
        cpu.write_file(SFR_ADCON0, (3 << 3) | 0x05)
        self.assertEqual(cpu.ram[SFR_ADRESH], 0x02)
        self.assertEqual(cpu.ram[SFR_ADRESL], 0xAB)
        self.assertFalse(cpu.ram[SFR_ADCON0] & 0x04)
        cpu.ram[SFR_ADCON1] = 0x00
        cpu.write_file(SFR_ADCON0, (3 << 3) | 0x05)
        self.assertEqual(cpu.ram[SFR_ADRESH], 0xAA)
        self.assertEqual(cpu.ram[SFR_ADRESL], 0xC0)

    def test_cr02_handler_trace_captures_ports_and_gpio_effect(self):
        cpu = self.firmware_cpu()
        cpu.run(10_000)
        cpu.set_gpio_bit("PORTD", 1, True)
        result = execute_request(
            cpu,
            b"CR02",
            step_limit=100_000,
            handler_pc=CR_HANDLER_MATRIX["2.71"][2],
            formatter_pc=RESPONSE_FORMATTERS["2.71"],
        )
        self.assertIsNone(result.error)
        self.assertTrue(result.handler_seen)
        self.assertTrue(result.formatter_seen)
        self.assertEqual(result.response, b"CR0220\n")
        read_addresses = {
            item.address for item in result.accesses if item.action == "read"
        }
        self.assertIn(SFR_PORTD, read_addresses)
        self.assertIn(SFR_PORTE, read_addresses)

    def test_synthetic_internal_eeprom_executes_a_unit_read(self):
        fixture = synthetic_controller_eeprom(7)
        self.assertEqual(calculate_fixture_checksum(7, fixture), int.from_bytes(fixture[:2], "big"))
        cpu = self.firmware_cpu()
        cpu.run(10_000)
        result = execute_request(cpu, b"AR03", step_limit=100_000)
        self.assertIsNone(result.error)
        self.assertEqual(result.response, b"AR0345\n")
        self.assertTrue(
            any(
                event.kind == "eeprom_read" and event.detail == "EEPROM[0x03]"
                for event in result.events
            )
        )

    def test_real_formatter_uses_lowercase_address_hex(self):
        cpu = self.firmware_cpu()
        cpu.run(10_000)
        result = execute_request(cpu, b"CR0A", step_limit=100_000)
        self.assertIsNone(result.error)
        self.assertEqual(result.response, b"CR0a00\n")
