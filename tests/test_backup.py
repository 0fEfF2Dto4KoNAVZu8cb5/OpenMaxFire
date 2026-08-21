import json
import tempfile
import unittest
from pathlib import Path

from openmaxfire.backup import build_eeprom_backup, save_json_document
from openmaxfire.client import StoveIdentity
from openmaxfire.protocol import calculate_configuration_checksum


class BackupTests(unittest.TestCase):
    def fixture(self):
        values = {address: 0 for address in range(0x100)}
        values[0x02] = 0x07
        for first, raw in (
            (0x03, b"00005215"),
            (0x0B, b"20051201"),
            (0x13, b"MAXFIRE 115     "),
        ):
            for offset, value in enumerate(raw):
                values[first + offset] = value
        checksum = calculate_configuration_checksum(7, values)
        values[0x00] = checksum >> 8
        values[0x01] = checksum & 0xFF
        identity = StoveIdentity(0, 7, 2, 0x71, 0, 0)
        return identity, values

    def test_complete_backup_is_lossless_and_checksum_verified(self):
        identity, values = self.fixture()
        backup = build_eeprom_backup(
            identity,
            values,
            port="COM7",
            baudrate=19200,
            created_utc="2026-08-21T00:00:00+00:00",
        )
        self.assertTrue(backup["checksum"]["matches"])
        self.assertEqual(backup["individualization"]["serial_number"], "00005215")
        self.assertEqual(backup["eeprom"]["AFF"], "00")
        self.assertEqual(len(backup["raw_hex"]), 512)

    def test_incomplete_backup_is_rejected(self):
        identity, values = self.fixture()
        del values[0x80]
        with self.assertRaisesRegex(ValueError, "A80"):
            build_eeprom_backup(identity, values, port="COM7", baudrate=19200)

    def test_backup_writer_refuses_silent_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "backup.json"
            save_json_document({"first": True}, path)
            with self.assertRaises(FileExistsError):
                save_json_document({"second": True}, path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"first": True})


if __name__ == "__main__":
    unittest.main()
