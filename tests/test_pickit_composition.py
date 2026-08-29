import hashlib
import json
import unittest
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

from openmaxfire.firmware import FirmwareImage, FirmwareImageError, parse_intel_hex
from openmaxfire.pickit import compose_pickit_image, serialize_intel_hex


ROOT = Path(__file__).resolve().parents[1]
FW202_PICKIT = (
    ROOT
    / "reverse-engineering/firmware/2.02/extracted/"
    "Bixby_0202_260827_PICkit.hex"
)
FW206_DOWNLOADER = (
    ROOT
    / "reverse-engineering/firmware/2.06/extracted/"
    "Bixby_02060021_Downloader.hex"
)
FW206_PICKIT = (
    ROOT
    / "reverse-engineering/firmware/2.06/extracted/"
    "Bixby_02060021_PICkit.hex"
)
FW270 = (
    ROOT
    / "reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex"
)
FW271 = (
    ROOT
    / "reverse-engineering/firmware/2.71/extracted/Bixby_0271_080315.hex"
)


class PickitCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fw202_pickit = FirmwareImage.load(FW202_PICKIT)
        cls.fw206_downloader = FirmwareImage.load(FW206_DOWNLOADER)
        cls.fw206_pickit = FirmwareImage.load(FW206_PICKIT)
        cls.fw270 = FirmwareImage.load(FW270)
        cls.fw271 = FirmwareImage.load(FW271)

    def test_intel_hex_serializer_round_trips_sparse_extended_memory(self):
        memory = {0x0000: 0x12, 0x0001: 0x34, 0x10000: 0x56}
        text = serialize_intel_hex(memory, record_size=16)
        parsed = parse_intel_hex(text)
        self.assertEqual(dict(parsed.memory), memory)
        self.assertEqual(parsed.record_counts[0x04], 2)
        self.assertTrue(text.endswith(":00000001FF\n"))

    def test_factory_206_pair_is_an_exact_golden_loader_overlay(self):
        composed = compose_pickit_image(
            self.fw206_pickit,
            [self.fw206_downloader],
        )
        output = composed.to_firmware_image(
            filename="Bixby_02060021_Derived_PICkit.hex"
        )
        self.assertEqual(output.program_words, self.fw206_pickit.program_words)
        self.assertEqual(output.user_id_words, self.fw206_pickit.user_id_words)
        self.assertEqual(
            output.configuration_word,
            self.fw206_pickit.configuration_word,
        )
        self.assertEqual(output.eeprom_words, self.fw206_pickit.eeprom_words)
        self.assertEqual(composed.steps[0].changed_words, 0)
        self.assertEqual(composed.steps[0].relocated_words, 4)
        self.assertEqual(composed.steps[0].protected_skipped_words, 0)

    def test_serial_5215_sequence_preserves_non_j3_sections(self):
        composed = compose_pickit_image(
            self.fw202_pickit,
            [self.fw206_downloader, self.fw270, self.fw271],
        )
        output = composed.to_firmware_image(
            filename="Bixby_0271_080315_Derived_PICkit_serial5215_precal.hex"
        )
        self.assertEqual(output.firmware_version, "2.71")
        self.assertEqual(len(output.program_words), 0x2000)
        self.assertEqual(
            [output.program_words[address] for address in range(4)],
            [self.fw202_pickit.program_words[address] for address in range(4)],
        )
        self.assertEqual(output.user_id_words, self.fw202_pickit.user_id_words)
        self.assertEqual(
            output.configuration_word,
            self.fw202_pickit.configuration_word,
        )
        self.assertEqual(output.eeprom_words, self.fw202_pickit.eeprom_words)
        for address in range(0x1E80, 0x2000):
            if not 0x1E84 <= address <= 0x1E87:
                self.assertEqual(
                    output.program_words[address],
                    self.fw202_pickit.program_words[address],
                )
        self.assertEqual(
            [output.program_words[address] for address in range(0x1E84, 0x1E88)],
            [self.fw271.program_words[address] for address in range(4)],
        )

    def test_serial_5215_206_prediction_retains_expected_sparse_words(self):
        composed = compose_pickit_image(
            self.fw202_pickit,
            [self.fw206_downloader],
        )
        output = composed.to_firmware_image(
            filename="Bixby_02060021_Derived_PICkit_serial5215_precal.hex"
        )
        differences = [
            address
            for address in range(0x2000)
            if output.program_words[address]
            != self.fw206_pickit.program_words[address]
        ]
        self.assertEqual(len(differences), 111)
        self.assertTrue(all(address < 0x1E80 for address in differences))

    def test_manifest_marks_image_as_derived_and_precalibration(self):
        composed = compose_pickit_image(
            self.fw206_pickit,
            [self.fw270],
        )
        manifest = composed.to_manifest(
            output_filename="Bixby_0270_070206_Derived_PICkit_factory206_precal.hex"
        )
        self.assertFalse(manifest["vendor_supplied"])
        self.assertTrue(manifest["calibration_required"])
        self.assertTrue(
            manifest["verification"]["physical_reset_vector_preserved"]
        )
        self.assertTrue(manifest["verification"]["eeprom_preserved"])
        self.assertEqual(
            manifest["output"]["sha256"],
            hashlib.sha256(composed.to_intel_hex().encode("ascii")).hexdigest(),
        )

    def test_incomplete_base_and_downloader_eeprom_fail_closed(self):
        incomplete_words = dict(self.fw206_pickit.program_words)
        del incomplete_words[0x100]
        incomplete = replace(
            self.fw206_pickit,
            program_words=MappingProxyType(incomplete_words),
        )
        with self.assertRaisesRegex(FirmwareImageError, "8,192 program words"):
            compose_pickit_image(incomplete, [self.fw270])

        with_eeprom = replace(
            self.fw270,
            eeprom_words=MappingProxyType({0: 0x12}),
        )
        with self.assertRaisesRegex(FirmwareImageError, "contains EEPROM"):
            compose_pickit_image(self.fw206_pickit, [with_eeprom])

    def test_committed_derived_images_match_manifest_and_regeneration(self):
        derived = ROOT / "reverse-engineering/firmware/derived-pickit"
        project = json.loads((derived / "manifest.json").read_text())
        self.assertEqual(project["physical_post_j3_readback_comparison"], "pending")
        golden = project["factory_2_06_golden_pair"]
        self.assertTrue(golden["mapped_memory"])
        self.assertTrue(golden["program"])
        self.assertTrue(golden["user_ids"])
        self.assertTrue(golden["configuration"])
        self.assertTrue(golden["eeprom"])
        self.assertEqual(len(project["images"]), 5)
        for document in project["images"]:
            base = FirmwareImage.load(ROOT / document["source_paths"]["base"])
            sequence = [
                FirmwareImage.load(ROOT / path)
                for path in document["source_paths"]["loader_sequence"]
            ]
            payload = compose_pickit_image(base, sequence).to_intel_hex().encode(
                "ascii"
            )
            output = ROOT / document["output"]["path"]
            self.assertEqual(output.read_bytes(), payload)
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                document["output"]["sha256"],
            )


if __name__ == "__main__":
    unittest.main()
