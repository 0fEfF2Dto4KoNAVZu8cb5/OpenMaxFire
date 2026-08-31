import unittest
from pathlib import Path

from tools.firmware_pipeline import CW_EXIT_PC, CW_HANDLER_MATRIX, parse_ihex
from tools.pic14_emulator import (
    PIC16F877A,
    execute_request,
    execute_silent_write,
    execute_telemetry_slot,
    probe_image,
    requested_telemetry_line,
    synthetic_controller_eeprom,
)


ROOT = Path(__file__).resolve().parents[1]


class WriteAndTelemetryExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        image = parse_ihex(
            (
                ROOT
                / "reverse-engineering/firmware/2.71/extracted/"
                "Bixby_0271_080315.hex"
            ).read_bytes()
        )
        cls.booted = PIC16F877A(
            image, data_eeprom=synthetic_controller_eeprom(7)
        )
        cls.booted.run(250_000)

    def execute_write(self, register: int, value: int, limit: int = 30_000):
        return execute_silent_write(
            self.booted.clone(),
            f"CW{register:02X}{value:02X}".encode("ascii"),
            step_limit=limit,
            handler_pc=CW_HANDLER_MATRIX["2.71"][register],
            exit_pc=CW_EXIT_PC["2.71"],
        )

    def test_remote_button_write_reaches_real_handler_and_silent_exit(self):
        result = self.execute_write(0x0E, 0x14)
        self.assertTrue(result.handler_seen)
        self.assertTrue(result.exit_seen)
        self.assertIsNone(result.error)
        self.assertIn((0x052, 0x00, 0x14), result.net_changes)

    def test_checksum_write_uses_modeled_pic_data_eeprom(self):
        result = self.execute_write(0x01, 0x00)
        events = [item for item in result.events if item.kind == "eeprom_write"]
        self.assertTrue(result.exit_seen)
        self.assertEqual(len(events), 2)
        self.assertIn("EEPROM[0x00]", events[0].detail)
        self.assertIn("EEPROM[0x01]", events[1].detail)

    def test_non_key_cw0f_value_returns_without_reset(self):
        result = self.execute_write(0x0F, 0x00)
        self.assertTrue(result.handler_seen)
        self.assertTrue(result.exit_seen)
        self.assertIsNone(result.error)

    def test_forced_t09_slot_runs_real_sender(self):
        result = execute_telemetry_slot(self.booted.clone(), "2.71", 0x09)
        self.assertTrue(result.sender_seen)
        self.assertIsNone(result.error)
        self.assertRegex(result.response, rb"^T09[0-9a-fA-F]{2}\n$")

    def test_loader_ea_ed_rehearsal_returns_eb_e4_without_eeprom_write(self):
        summary, _, events = probe_image(
            ROOT
            / "reverse-engineering/firmware/2.02/extracted/"
            "Bixby_0202_260827_PICkit.hex",
            "loader-rehearsal",
            b"\xEA\xED",
            "non-writing loader entry and handoff",
            boot_steps=0,
            probe_steps=200_000,
        )
        self.assertIsNone(summary["error"])
        self.assertEqual(summary["tx_hex"], "EB E4")
        self.assertEqual(summary["uart_rx_events"], 2)
        self.assertEqual(summary["uart_tx_events"], 2)
        self.assertFalse(any(item.kind == "eeprom_write" for item in events))

    def test_all_derived_pickit_images_boot_and_answer_cr00(self):
        root = ROOT / "reverse-engineering/firmware/derived-pickit"
        images = sorted(root.glob("*/*.hex"))
        self.assertEqual(len(images), 5)
        for image in images:
            with self.subTest(image=image.name):
                summary, _, _ = probe_image(
                    image,
                    image.stem,
                    b"CR00",
                    "derived PICkit application boot probe",
                    boot_steps=250_000,
                    probe_steps=500_000,
                )
                self.assertIsNone(summary["error"])
                self.assertEqual(summary["tx_ascii"], "CR0000\\x0A")


class Firmware202CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = parse_ihex(
            (
                ROOT
                / "reverse-engineering/firmware/2.02/extracted/"
                "Bixby_0202_260827_PICkit.hex"
            ).read_bytes()
        )
        cls.booted = PIC16F877A(
            cls.image, data_eeprom=synthetic_controller_eeprom(4)
        )
        for _ in range(250_000):
            if cls.booted.pc == 0x191F:
                cls.booted.ram[0x04C] = 0x20
                break
            cls.booted.step()
        else:
            raise AssertionError("2.02 did not reach its first state dispatch")

    def test_cr_constants_and_generic_high_register_responses(self):
        expected = {
            0x00: b"CR0000\n",
            0x08: b"CR0804\n",
            0x0C: b"CR0c02\n",
            0x0D: b"CR0d00\n",
            0x0E: b"CR0e00\n",
        }
        for register, response in expected.items():
            with self.subTest(register=register):
                result = execute_request(
                    self.booted.clone(),
                    f"CR{register:02X}".encode("ascii"),
                    step_limit=20_000,
                )
                self.assertIsNone(result.error)
                self.assertEqual(result.response, response)

    def test_cw0e_remote_button_reaches_format04_handler(self):
        result = execute_silent_write(
            self.booted.clone(),
            b"CW0E14",
            step_limit=20_000,
            handler_pc=CW_HANDLER_MATRIX["2.02"][0x0E],
            exit_pc=CW_EXIT_PC["2.02"],
        )
        self.assertTrue(result.handler_seen)
        self.assertTrue(result.exit_seen)
        self.assertIsNone(result.error)
        self.assertIn((0x051, 0x00, 0x14), result.net_changes)

    def test_format04_has_no_cw0f_dispatch_entry(self):
        handlers = CW_HANDLER_MATRIX["2.02"]
        self.assertEqual(len(handlers), 0x0F)
        self.assertEqual(self.image.words[0x12E5 + 4 + 0x0F], 0x0000)

    def test_format04_state_and_last_telemetry_slots_complete(self):
        state = execute_telemetry_slot(self.booted.clone(), "2.02", 0x0C)
        last = execute_telemetry_slot(self.booted.clone(), "2.02", 0x15)
        self.assertIsNone(state.error)
        self.assertIn(b"T0c20\n", state.response)
        self.assertIsNone(last.error)
        self.assertRegex(last.response, rb"T15[0-9a-fA-F]{2}\n$")
        self.assertEqual(
            requested_telemetry_line(last.response, 0x15),
            last.response.splitlines()[-1],
        )


if __name__ == "__main__":
    unittest.main()
