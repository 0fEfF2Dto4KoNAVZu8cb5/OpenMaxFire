import importlib.util
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "firmware_pipeline", ROOT / "tools" / "firmware_pipeline.py"
)
firmware_pipeline = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = firmware_pipeline
SPEC.loader.exec_module(firmware_pipeline)


class FirmwarePipelineTests(unittest.TestCase):
    def test_all_preserved_images_parse_and_decode(self):
        for image_spec in firmware_pipeline.IMAGE_SPECS:
            raw = (ROOT / image_spec.extracted_path).read_bytes()
            image = firmware_pipeline.parse_ihex(raw)
            program = {
                address: word for address, word in image.words.items()
                if firmware_pipeline.region_for_word(address) == "program"
            }
            self.assertTrue(program)
            self.assertFalse([
                address for address, word in program.items()
                if firmware_pipeline.decode_pic14(word).kind == "unknown"
            ])

    def test_embedded_271_extraction_matches_preserved_copy(self):
        package_path = ROOT / "preservation/original/vendor-packages/BixCheck_080315.zip"
        with zipfile.ZipFile(package_path) as package:
            executable = package.read("BixCheck_080315.exe")
        payload, metadata = firmware_pipeline.extract_ascii_hex_payload(
            executable, "Bixby_0271_080315.hex"
        )
        self.assertEqual(
            payload,
            (ROOT / "reverse-engineering/firmware/2.71/extracted/Bixby_0271_080315.hex").read_bytes(),
        )
        self.assertEqual(metadata["decoded_bytes"], 42740)

    def test_checksum_failure_is_rejected(self):
        with self.assertRaises(firmware_pipeline.FirmwareError):
            firmware_pipeline.parse_ihex(b":020000000000FF\n:00000001FF\n")

    def test_known_pic14_opcodes(self):
        cases = {
            0x0009: "retfie",
            0x3018: "movlw",
            0x008A: "movwf",
            0x3C43: "sublw",
            0x2800: "goto",
            0x2000: "call",
        }
        for word, mnemonic in cases.items():
            self.assertEqual(firmware_pipeline.decode_pic14(word).mnemonic, mnemonic)

    def test_button_and_sensor_mux_signatures_match_all_generations(self):
        application_variants = {
            "2.06": "downloader",
            "2.70": "embedded",
            "2.71": "embedded",
        }
        for version, variant in application_variants.items():
            image_spec = next(
                item for item in firmware_pipeline.IMAGE_SPECS
                if item.version == version and item.variant == variant
            )
            image = firmware_pipeline.parse_ihex(
                (ROOT / image_spec.extracted_path).read_bytes()
            )
            expected = firmware_pipeline.MUX_SCAN_EXPECTED[version]
            self.assertEqual(
                firmware_pipeline.find_word_sequence(
                    image.words, firmware_pipeline.BUTTON_MUX_PATTERN
                ),
                [expected["front_panel"]],
            )
            self.assertEqual(
                firmware_pipeline.find_word_sequence(
                    image.words, firmware_pipeline.SENSOR_MUX_PATTERN
                ),
                [expected["external_sensors"]],
            )

    def test_j9_j10_sensor_path_signatures_match_all_generations(self):
        application_variants = {
            "2.06": "downloader",
            "2.70": "embedded",
            "2.71": "embedded",
        }
        for version, variant in application_variants.items():
            image_spec = next(
                item for item in firmware_pipeline.IMAGE_SPECS
                if item.version == version and item.variant == variant
            )
            image = firmware_pipeline.parse_ihex(
                (ROOT / image_spec.extracted_path).read_bytes()
            )
            for stage, pattern in firmware_pipeline.SENSOR_PATH_PATTERNS.items():
                self.assertEqual(
                    firmware_pipeline.find_masked_word_sequence(image.words, pattern),
                    [firmware_pipeline.SENSOR_PATH_EXPECTED[version][stage]],
                    f"{version} {stage}",
                )

    def test_cw_dispatch_tables_match_all_sixteen_handlers(self):
        application_variants = {
            "2.06": "downloader",
            "2.70": "embedded",
            "2.71": "embedded",
        }
        for version, variant in application_variants.items():
            image_spec = next(
                item for item in firmware_pipeline.IMAGE_SPECS
                if item.version == version and item.variant == variant
            )
            image = firmware_pipeline.parse_ihex(
                (ROOT / image_spec.extracted_path).read_bytes()
            )
            dispatch = firmware_pipeline.CW_DISPATCH_PC[version]
            handlers = firmware_pipeline.CW_HANDLER_MATRIX[version]
            self.assertEqual(len(handlers), 16)
            for register, handler in enumerate(handlers):
                word = image.words[dispatch + 4 + register]
                self.assertEqual(
                    firmware_pipeline.decode_pic14(word).mnemonic,
                    "goto",
                    f"{version} CW{register:02X}",
                )
                self.assertEqual(word & 0x07FF, handler & 0x07FF)

    def test_periodic_telemetry_sender_anchors(self):
        application_variants = {
            "2.06": "downloader",
            "2.70": "embedded",
            "2.71": "embedded",
        }
        for version, variant in application_variants.items():
            image_spec = next(
                item for item in firmware_pipeline.IMAGE_SPECS
                if item.version == version and item.variant == variant
            )
            image = firmware_pipeline.parse_ihex(
                (ROOT / image_spec.extracted_path).read_bytes()
            )
            path = firmware_pipeline.TELEMETRY_PATHS[version]
            self.assertEqual(image.words[path["t_sender"]], 0x3054)
            self.assertEqual(
                firmware_pipeline.decode_pic14(image.words[path["t_call"]]).mnemonic,
                "call",
            )

    def test_t09_state_family_dispatchers(self):
        application_variants = {
            "2.06": "downloader",
            "2.70": "embedded",
            "2.71": "embedded",
        }
        for version, variant in application_variants.items():
            image_spec = next(
                item for item in firmware_pipeline.IMAGE_SPECS
                if item.version == version and item.variant == variant
            )
            image = firmware_pipeline.parse_ihex(
                (ROOT / image_spec.extracted_path).read_bytes()
            )
            dispatch = firmware_pipeline.STATE_DISPATCH_PC[version]
            self.assertEqual(image.words[dispatch], 0x084C)
            self.assertEqual(image.words[dispatch + 1], 0x3970)
            for offset, handler in zip(
                (3, 6, 9, 12, 15, 18, 21, 24),
                firmware_pipeline.STATE_FAMILY_HANDLERS[version],
                strict=True,
            ):
                word = image.words[dispatch + offset]
                self.assertEqual(
                    firmware_pipeline.decode_pic14(word).mnemonic, "goto"
                )
                self.assertEqual(word & 0x07FF, handler & 0x07FF)


if __name__ == "__main__":
    unittest.main()
