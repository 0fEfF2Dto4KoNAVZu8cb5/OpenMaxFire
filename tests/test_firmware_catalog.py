import json
import tempfile
import unittest
from pathlib import Path

from openmaxfire.firmware import FirmwareVariant
from openmaxfire.firmware_catalog import (
    FIRMWARE_CORPUS,
    FirmwareCorpusEntry,
    validate_firmware_corpus,
)


class FirmwareCorpusTests(unittest.TestCase):
    def test_catalog_matches_preserved_index(self):
        self.assertEqual(len(FIRMWARE_CORPUS), 5)
        self.assertEqual(
            {item.firmware_version for item in FIRMWARE_CORPUS},
            {"2.02", "2.06", "2.70", "2.71"},
        )
        self.assertEqual(
            sum(item.variant is FirmwareVariant.PICKIT for item in FIRMWARE_CORPUS),
            2,
        )

    def test_missing_and_tampered_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = validate_firmware_corpus(directory)
            self.assertFalse(missing.valid)
            self.assertEqual(missing.present_count, 0)

            path = Path(directory) / "sample.hex"
            path.write_text(":00000001FF\n")
            catalog = (
                FirmwareCorpusEntry(
                    "sample.hex",
                    "sample.hex",
                    "2.71",
                    FirmwareVariant.EMBEDDED,
                    "0" * 64,
                    path.stat().st_size,
                    0,
                    0x3F72,
                ),
            )
            tampered = validate_firmware_corpus(directory, catalog=catalog)
        self.assertFalse(tampered.valid)
        self.assertIn("SHA-256 mismatch", tampered.results[0].errors)

    def test_repository_corpus_validates_when_present(self):
        root = Path(__file__).resolve().parents[1]
        if not all((root / item.relative_path).is_file() for item in FIRMWARE_CORPUS):
            self.skipTest("firmware corpus is omitted from this API-only work export")
        report = validate_firmware_corpus(root)
        self.assertTrue(report.valid, report.to_dict())

    def test_recovered_202_dump_matches_prior_live_eeprom_and_known_loader(self):
        root = Path(__file__).resolve().parents[1]
        recovered = next(
            item for item in FIRMWARE_CORPUS if item.firmware_version == "2.02"
        )
        known_loader = next(
            item
            for item in FIRMWARE_CORPUS
            if item.firmware_version == "2.06"
            and item.variant is FirmwareVariant.PICKIT
        )
        recovered_image = validate_firmware_corpus(
            root, catalog=(recovered,)
        ).results[0].image
        known_loader_image = validate_firmware_corpus(
            root, catalog=(known_loader,)
        ).results[0].image
        self.assertIsNotNone(recovered_image)
        self.assertIsNotNone(known_loader_image)
        for address in range(0x1E80, 0x2000):
            self.assertEqual(
                recovered_image.program_words[address],
                known_loader_image.program_words[address],
            )

        backup = json.loads(
            (
                root
                / "research/live/2026-08-22-fw202-format04/"
                "maxfire-fw202-format04-eeprom.json"
            ).read_text(encoding="utf-8")
        )
        expected = {
            int(address[1:], 16): int(value, 16)
            for address, value in backup["eeprom"].items()
        }
        self.assertEqual(dict(recovered_image.eeprom_words), expected)


if __name__ == "__main__":
    unittest.main()
