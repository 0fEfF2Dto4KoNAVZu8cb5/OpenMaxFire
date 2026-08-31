import hashlib
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
            "2.02": "pickit",
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
            patterns = firmware_pipeline.MUX_SCAN_PATTERNS[version]
            self.assertEqual(
                firmware_pipeline.find_word_sequence(
                    image.words, patterns["front_panel"]
                ),
                [expected["front_panel"]],
            )
            self.assertEqual(
                firmware_pipeline.find_word_sequence(
                    image.words, patterns["external_sensors"]
                ),
                [expected["external_sensors"]],
            )

    def test_j9_j10_sensor_path_signatures_match_all_generations(self):
        application_variants = {
            "2.02": "pickit",
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
                pattern = firmware_pipeline.SENSOR_PATH_PATTERN_OVERRIDES.get(
                    version, {}
                ).get(stage, pattern)
                self.assertEqual(
                    firmware_pipeline.find_masked_word_sequence(image.words, pattern),
                    [firmware_pipeline.SENSOR_PATH_EXPECTED[version][stage]],
                    f"{version} {stage}",
                )

    def test_202_j9_interval_direct_writers_distinguish_runtime_latch(self):
        image = firmware_pipeline.parse_ihex(
            (
                ROOT
                / "preservation/original/firmware/2.02/"
                "Bixby_0202_260827_PICkit.hex"
            ).read_bytes()
        )
        direct_writes = {
            address: word
            for address, word in image.words.items()
            if firmware_pipeline.region_for_word(address) == "program"
            and word in (0x00C4, 0x00C5)
        }
        self.assertEqual(
            direct_writes,
            {
                0x0CD4: 0x00C5,
                0x0CD6: 0x00C4,
                0x0CDF: 0x00C5,
                0x0CE1: 0x00C4,
                0x1853: 0x00C5,
                0x1855: 0x00C4,
            },
        )
        self.assertEqual(
            tuple(image.words[address] for address in range(0x0CD2, 0x0CD7)),
            (0x1003, 0x0C47, 0x00C5, 0x0C46, 0x00C4),
        )
        self.assertEqual(
            tuple(image.words[address] for address in range(0x0CDE, 0x0CE2)),
            (0x3001, 0x00C5, 0x3068, 0x00C4),
        )
        self.assertEqual(
            tuple(image.words[address] for address in range(0x1852, 0x1856)),
            (0x3002, 0x00C5, 0x30D0, 0x00C4),
        )
        self.assertEqual((0x0168 >> 4) & 0xFF, 0x16)
        self.assertEqual((0x02D0 >> 4) & 0xFF, 0x2D)

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

    def test_original_202_has_no_cw0f_reset_handler_but_206_does(self):
        image_paths = {
            "2.02": ROOT / "preservation/original/firmware/2.02/Bixby_0202_260827_PICkit.hex",
            "2.06": ROOT / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex",
        }
        expected_hashes = {
            "2.02": "272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab",
            "2.06": "2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4",
        }
        images = {}
        for version, path in image_paths.items():
            raw = path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_hashes[version])
            images[version] = firmware_pipeline.parse_ihex(raw)

        original = images["2.02"]
        original_dispatch = 0x12E5
        self.assertEqual(
            tuple(original.words[original_dispatch + offset] for offset in range(4)),
            (0x100A, 0x148A, 0x110A, 0x0782),
        )
        for register in range(0x0F):
            self.assertEqual(
                firmware_pipeline.decode_pic14(
                    original.words[original_dispatch + 4 + register]
                ).mnemonic,
                "goto",
                f"2.02 CW{register:02X}",
            )
        self.assertEqual(original_dispatch + 4 + 0x0F, 0x12F8)
        self.assertEqual(
            firmware_pipeline.decode_pic14(original.words[0x12F8]).mnemonic,
            "nop",
        )
        self.assertEqual(
            tuple(original.words[address] for address in range(0x12F8, 0x12FB)),
            (0x0000, 0x0000, 0x0000),
        )
        self.assertEqual(
            [
                address
                for address, word in original.words.items()
                if firmware_pipeline.region_for_word(address) == "program"
                and word == 0x3CC4
            ],
            [],
        )

        updated = images["2.06"]
        updated_dispatch = firmware_pipeline.CW_DISPATCH_PC["2.06"]
        cw0f = updated.words[updated_dispatch + 4 + 0x0F]
        self.assertEqual(cw0f, 0x290B)
        self.assertEqual(firmware_pipeline.decode_pic14(cw0f).mnemonic, "goto")
        self.assertEqual(cw0f & 0x07FF, 0x110B & 0x07FF)
        self.assertEqual(updated.words[0x110D], 0x3CC4)
        self.assertEqual(updated.words[0x1138], 0x018A)
        self.assertEqual(updated.words[0x1139], 0x2800)

    def test_periodic_telemetry_sender_anchors(self):
        application_variants = {
            "2.02": "pickit",
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

    def test_nonperiodic_t20_event_paths_exist_in_all_later_generations(self):
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
            path = firmware_pipeline.EVENT_T20_PATHS[version]
            sequence = tuple(path["sequence"])
            self.assertEqual(
                tuple(
                    image.words[path["entry"] + offset]
                    for offset in range(len(sequence))
                ),
                sequence,
                version,
            )
            call = image.words[path["entry"] + len(sequence) - 1]
            self.assertEqual(call & 0x07FF, path["sender"] & 0x07FF)

        self.assertNotIn("2.02", firmware_pipeline.EVENT_T20_PATHS)

    def test_state_family_dispatchers(self):
        application_variants = {
            "2.02": "pickit",
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
                firmware_pipeline.STATE_BRANCH_OFFSETS[version],
                firmware_pipeline.STATE_FAMILY_HANDLERS[version],
                strict=True,
            ):
                word = image.words[dispatch + offset]
                self.assertEqual(
                    firmware_pipeline.decode_pic14(word).mnemonic, "goto"
                )
                self.assertEqual(word & 0x07FF, handler & 0x07FF)

    def test_206_cooldown_timer_and_off_threshold(self):
        image_spec = next(
            item for item in firmware_pipeline.IMAGE_SPECS
            if item.version == "2.06" and item.variant == "downloader"
        )
        image = firmware_pipeline.parse_ihex(
            (ROOT / image_spec.extracted_path).read_bytes()
        )

        # CCPR1=0xC674, CCP1CON=0x0B (special-event compare), and
        # T1CON=0x31 (Fosc/4, 1:8 prescale). The special event resets Timer1
        # and raises the flag consumed by the increment path below.
        self.assertEqual(
            tuple(image.words[address] for address in range(0x0236, 0x023E)),
            (0x3074, 0x0095, 0x30C6, 0x0096,
             0x300B, 0x0097, 0x3031, 0x0090),
        )
        self.assertEqual(
            tuple(image.words[address] for address in range(0x08AF, 0x08B3)),
            (0x0FCA, 0x28B3, 0x0F4B, 0x00CB),
        )

        # Cooldown remains active through 0x1517 and installs Off (0x20)
        # after the counter reaches 0x1518, subject to the adjacent sensor
        # predicates. At the photographed 10 MHz oscillator this is 877.893 s.
        self.assertEqual(
            tuple(image.words[address] for address in range(0x194B, 0x1960)),
            (
                0x084B, 0x3C15, 0x1C03, 0x2956, 0x1D03, 0x2955, 0x084A,
                0x3C17, 0x1C03, 0x2956, 0x2E25, 0x0857, 0x3C13, 0x1803,
                0x295B, 0x2E25, 0x1ED6, 0x295E, 0x2E25, 0x3020, 0x00CC,
            ),
        )
        event_seconds = 0xC674 / (10_000_000 / 4 / 8)
        self.assertAlmostEqual(event_seconds * 0x1518, 877.89312)


if __name__ == "__main__":
    unittest.main()
