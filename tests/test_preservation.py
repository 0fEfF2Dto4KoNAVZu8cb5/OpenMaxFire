import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openmaxfire.firmware import FirmwareImage
from openmaxfire.preservation import (
    ProtectionState,
    compare_pic16f877a_dumps,
    inspect_pic16f877a_dump,
)


def record(address, record_type, payload=b""):
    body = bytes(
        [len(payload), (address >> 8) & 0xFF, address & 0xFF, record_type]
    ) + payload
    return ":" + (body + bytes([(-sum(body)) & 0xFF])).hex().upper()


def dump_text(*, config=0x3F72, eeprom=b"\x12\x00\x34\x00", split=False):
    program = (
        (record(0, 0, b"\x01\x10"), record(2, 0, b"\x02\x10"))
        if split
        else (record(0, 0, b"\x01\x10\x02\x10"),)
    )
    return "\n".join(
        program
        + (
            record(0x4000, 0, b"\x01\x00\x02\x00\x03\x00\x04\x00"),
            record(0x400C, 0, b"\x2A\x0E"),
            record(0x400E, 0, bytes((config & 0xFF, config >> 8))),
            record(0x4200, 0, eeprom),
            record(0, 1),
        )
    )


class PicPreservationTests(unittest.TestCase):
    def test_semantic_comparison_accepts_different_hex_record_layouts(self):
        first = FirmwareImage.parse(dump_text(), filename="read-01.hex")
        second = FirmwareImage.parse(
            dump_text(split=True), filename="read-02.hex"
        )
        report = compare_pic16f877a_dumps((first, second))
        self.assertTrue(report.authenticated)
        self.assertTrue(report.program_matches)
        self.assertTrue(report.eeprom_matches)
        self.assertFalse(report.raw_files_identical)
        self.assertEqual(
            report.inspections[0].program_code_protection,
            ProtectionState.DISABLED,
        )
        self.assertEqual(
            report.inspections[0].eeprom_code_protection,
            ProtectionState.DISABLED,
        )
        self.assertTrue(report.inspections[0].device_id_matches)

    def test_any_memory_difference_blocks_authentication(self):
        first = FirmwareImage.parse(dump_text(), filename="read-01.hex")
        second = FirmwareImage.parse(
            dump_text(eeprom=b"\x13\x00\x34\x00"), filename="read-02.hex"
        )
        report = compare_pic16f877a_dumps((first, second))
        self.assertFalse(report.authenticated)
        self.assertFalse(report.eeprom_matches)
        self.assertIn("data EEPROM differs", " ".join(report.blockers))

    def test_code_protection_or_missing_configuration_fails_closed(self):
        protected = inspect_pic16f877a_dump(
            FirmwareImage.parse(dump_text(config=0x1E72), filename="protected.hex")
        )
        self.assertEqual(
            protected.program_code_protection, ProtectionState.ENABLED
        )
        self.assertEqual(
            protected.eeprom_code_protection, ProtectionState.ENABLED
        )
        self.assertFalse(protected.safe_read)

        missing = "\n".join(
            (
                record(0, 0, b"\x01\x10"),
                record(0x4200, 0, b"\x12\x00"),
                record(0, 1),
            )
        )
        unknown = inspect_pic16f877a_dump(
            FirmwareImage.parse(missing, filename="missing-config.hex")
        )
        self.assertEqual(
            unknown.program_code_protection, ProtectionState.UNKNOWN
        )
        self.assertFalse(unknown.safe_read)

    def test_cli_writes_machine_readable_manifest_and_refuses_replacement(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            first = temp / "read-01.hex"
            second = temp / "read-02.hex"
            output = temp / "manifest.json"
            first.write_text(dump_text(), encoding="ascii")
            second.write_text(dump_text(split=True), encoding="ascii")
            command = [
                sys.executable,
                str(root / "tools" / "pickit_preservation.py"),
                str(first),
                str(second),
                "--output",
                str(output),
            ]
            completed = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(json.loads(output.read_text())["authenticated"])
            repeated = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(repeated.returncode, 2)
            self.assertIn("File exists", repeated.stderr)


if __name__ == "__main__":
    unittest.main()
