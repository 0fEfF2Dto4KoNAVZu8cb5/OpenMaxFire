import unittest

from openmaxfire.firmware import (
    FirmwareImage,
    FirmwareImageError,
    FirmwareVariant,
    assess_firmware_compatibility,
    build_program_blocks,
    loader_state_machine_supported,
    parse_intel_hex,
)
from openmaxfire.profiles import PROFILES_BY_KEY


def record(address, record_type, payload=b""):
    body = bytes(
        [len(payload), (address >> 8) & 0xFF, address & 0xFF, record_type]
    ) + payload
    checksum = (-sum(body)) & 0xFF
    return ":" + (body + bytes([checksum])).hex().upper()


def fixture(name="Bixby_0271_080315.hex"):
    text = "\n".join(
        (
            record(0x0000, 0, b"\x34\x12\x78\x16"),
            record(0x400E, 0, b"\x72\x3F"),
            record(0, 1),
        )
    )
    return FirmwareImage.parse(text, filename=name)


class FirmwareApiTests(unittest.TestCase):
    def test_parser_validates_and_maps_pic_words(self):
        image = fixture()
        self.assertEqual(image.firmware_version, "2.71")
        self.assertEqual(image.variant, FirmwareVariant.EMBEDDED)
        self.assertEqual(image.program_words[0], 0x1234)
        self.assertEqual(image.program_words[1], 0x1678)
        self.assertEqual(image.configuration_word, 0x3F72)

    def test_version_token_wins_over_ambiguous_build_date(self):
        image = fixture("Bixby_0270_070206.hex")
        self.assertEqual(image.firmware_version, "2.70")
        self.assertEqual(image.variant, FirmwareVariant.EMBEDDED)

    def test_recovered_202_pickit_filename_is_identified(self):
        image = fixture("Bixby_0202_260827_PICkit.hex")
        self.assertEqual(image.firmware_version, "2.02")
        self.assertEqual(image.variant, FirmwareVariant.PICKIT)

    def test_loader_blocks_use_reconstructed_framing(self):
        block = build_program_blocks(fixture())[0]
        self.assertEqual(block.word_address, 0)
        self.assertEqual(block.data, b"\x34\x12\x78\x16")
        self.assertEqual(block.frame, b"\xE3\x00\x00\x04\xD4\x34\x12\x78\x16")

    def test_checksum_error_is_rejected(self):
        bad = record(0, 0, b"\x34\x12")[:-2] + "00\n" + record(0, 1)
        with self.assertRaisesRegex(FirmwareImageError, "checksum"):
            parse_intel_hex(bad)

    def test_pickit_image_is_not_j3_eligible(self):
        image = fixture("Bixby_02060021_PICkit.hex")
        result = assess_firmware_compatibility(
            image, PROFILES_BY_KEY["fw202-format04"]
        )
        self.assertFalse(result.j3_layout_eligible)
        self.assertFalse(result.valid_for_offline_planning)
        self.assertFalse(result.live_programming_supported)
        self.assertFalse(loader_state_machine_supported())

    def test_format_migration_is_reported_not_hidden(self):
        result = assess_firmware_compatibility(
            fixture(), PROFILES_BY_KEY["fw202-format04"]
        )
        self.assertTrue(result.valid_for_offline_planning)
        self.assertTrue(result.data_format_migration_required)
        self.assertIn("calibration migration", " ".join(result.warnings))


if __name__ == "__main__":
    unittest.main()
