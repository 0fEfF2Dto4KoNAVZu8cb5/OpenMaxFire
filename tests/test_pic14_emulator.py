import unittest
from pathlib import Path

from tools.firmware_pipeline import CW_EXIT_PC, CW_HANDLER_MATRIX, parse_ihex
from tools.pic14_emulator import (
    PIC16F877A,
    execute_silent_write,
    execute_telemetry_slot,
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


if __name__ == "__main__":
    unittest.main()
