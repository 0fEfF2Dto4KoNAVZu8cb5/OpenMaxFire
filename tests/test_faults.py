import unittest

from openmaxfire.faults import (
    FORMAT04_FAULT_PATTERNS,
    decode_format04_indicator_mask,
    indicator_lights,
)


class Format04FaultDecoderTests(unittest.TestCase):
    def test_all_eight_indicator_bits_use_one_based_light_numbers(self):
        self.assertEqual(indicator_lights(0x00), ())
        self.assertEqual(indicator_lights(0x81), (1, 8))
        self.assertEqual(indicator_lights(0xFF), tuple(range(1, 9)))

    def test_live_confirmed_feeder_wheel_pattern(self):
        fault = decode_format04_indicator_mask(0x80)
        self.assertTrue(fault.recognized)
        self.assertEqual(fault.lights, (8,))
        self.assertEqual(fault.code, "feeder_wheel_failure")
        self.assertIn("live-confirmed", fault.evidence)

    def test_light1_position_is_live_but_meaning_remains_factory_documented(self):
        fault = decode_format04_indicator_mask(0x01)
        self.assertEqual(fault.lights, (1,))
        self.assertEqual(fault.code, "power_interruption")
        self.assertIn("light position live-confirmed", fault.evidence)
        self.assertIn("meaning factory-documented", fault.evidence)

    def test_factory_documented_combination_is_lossless(self):
        fault = decode_format04_indicator_mask(0x06)
        self.assertEqual(fault.lights, (2, 3))
        self.assertEqual(fault.code, "empty_hopper_or_possible_blocked_flue")
        self.assertIn("inferred", fault.evidence)

    def test_unknown_combination_preserves_mask_and_lights(self):
        fault = decode_format04_indicator_mask(0x18)
        self.assertFalse(fault.recognized)
        self.assertEqual(fault.mask, 0x18)
        self.assertEqual(fault.lights, (4, 5))
        self.assertIsNone(fault.code)

    def test_pattern_table_keys_match_embedded_masks(self):
        self.assertTrue(FORMAT04_FAULT_PATTERNS)
        for mask, pattern in FORMAT04_FAULT_PATTERNS.items():
            with self.subTest(mask=mask):
                self.assertEqual(pattern.mask, mask)
                self.assertEqual(pattern.lights, indicator_lights(mask))

    def test_rejects_non_byte_masks(self):
        for value in (-1, 0x100, True, "80"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                indicator_lights(value)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
