import unittest

from openmaxfire.configuration import (
    ConfigurationImage,
    configuration_schema,
    plan_configuration_restore,
    plan_configuration_update,
)
from openmaxfire.profiles import PROFILES_BY_KEY


def image_for(profile_key="fw271-format07"):
    profile = PROFILES_BY_KEY[profile_key]
    raw = bytearray(256)
    raw[2] = profile.data_format
    raw[3:11] = b"00005215"
    raw[11:19] = b"01102007"
    raw[19:35] = b"Bixby Model 115 "
    return ConfigurationImage(bytes(raw)).with_checksum()


class ConfigurationApiTests(unittest.TestCase):
    def test_generated_schemas_match_recovered_adjustment_counts(self):
        format05 = configuration_schema(5)
        format07 = configuration_schema(7)
        self.assertEqual(len(format05.fields) - 5, 71)
        self.assertEqual(len(format07.fields) - 5, 82)

    def test_decodes_and_edits_shared_bit_fields_without_clobbering(self):
        image = image_for()
        updated = image.with_edits(
            {
                "fuel_a.ratio_ash_trimpot_mode": True,
                "fuel_a.disable_auto_restart": True,
            }
        )
        self.assertEqual(updated.raw[0x6E] & 0x03, 0x03)
        decoded = updated.decoded()
        self.assertTrue(decoded["fuel_a.ratio_ash_trimpot_mode"])
        self.assertTrue(decoded["fuel_a.disable_auto_restart"])
        self.assertTrue(updated.checksum_valid)

    def test_lean_burn_fields_use_wire_transforms(self):
        image = image_for().with_edits(
            {
                "fuel_a.lean_burn_threshold_percent": 50,
                "fuel_a.lean_burn_fan_percent": 30,
                "fuel_a.lean_burn_feed_percent": -30,
            }
        )
        self.assertEqual(image.raw[0x6B], 64)
        self.assertEqual(image.raw[0x6C], 167)
        self.assertEqual(image.raw[0x6D], 167)
        decoded = image.decoded()
        self.assertEqual(decoded["fuel_a.lean_burn_threshold_percent"], 50)
        self.assertEqual(decoded["fuel_a.lean_burn_fan_percent"], 30)
        self.assertEqual(decoded["fuel_a.lean_burn_feed_percent"], -30)

    def test_update_plan_writes_checksum_last_and_requires_full_verify(self):
        profile = PROFILES_BY_KEY["fw271-format07"]
        current = image_for()
        plan = plan_configuration_update(
            current, {"fuel_a.fan.level_1": 0x42}, profile
        )
        self.assertTrue(plan.has_writes)
        self.assertEqual(plan.operations[0].address, 0x40)
        self.assertEqual(plan.operations[-1].unit, "C")
        self.assertEqual(plan.operations[-1].address, 0x01)
        self.assertEqual(plan.operations[-1].value, 0x00)
        self.assertNotIn(0x00, [operation.address for operation in plan.operations if operation.unit == "A"])
        self.assertNotIn(0x01, [operation.address for operation in plan.operations if operation.unit == "A"])
        self.assertEqual(plan.verify_addresses, tuple(range(256)))
        self.assertFalse(plan.to_dict()["execution_supported"])

    def test_restore_preserves_identity_by_default(self):
        profile = PROFILES_BY_KEY["fw271-format07"]
        current = image_for()
        changed = bytearray(current.raw)
        changed[3] = ord("9")
        target = ConfigurationImage(bytes(changed)).with_checksum()
        with self.assertRaises(PermissionError):
            plan_configuration_restore(current, target, profile)

    def test_backup_document_import_is_lossless(self):
        image = image_for()
        restored = ConfigurationImage.from_backup_document(
            {"raw_hex": image.raw.hex().upper()}
        )
        self.assertEqual(restored, image)

    def test_invalid_ranges_and_read_only_fields_are_rejected(self):
        image = image_for()
        with self.assertRaises(ValueError):
            image.with_edits({"fuel_a.ash_dump_heat_level": 9})
        with self.assertRaises(PermissionError):
            image.with_edits({"serial_number": "123"})


if __name__ == "__main__":
    unittest.main()
