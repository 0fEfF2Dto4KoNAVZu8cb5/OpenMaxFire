import unittest

from openmaxfire.client import StoveIdentity
from openmaxfire.profiles import (
    Capability,
    CapabilityState,
    PROFILES,
    PROFILES_BY_KEY,
    profile_for_data_format,
    select_profile,
)


class ControllerProfileTests(unittest.TestCase):
    def test_all_known_pairings_select_exact_profiles(self):
        identities = (
            (StoveIdentity(0, 4, 2, 2, 0, 0), "fw202-format04"),
            (StoveIdentity(0, 5, 2, 6, 0, 0x21), "fw206-format05"),
            (StoveIdentity(0, 7, 2, 0x70, 0, 2), "fw270-format07"),
            (StoveIdentity(0, 7, 2, 0x71, 0, 0), "fw271-format07"),
        )
        for identity, key in identities:
            with self.subTest(key=key):
                self.assertEqual(select_profile(identity).key, key)
                self.assertEqual(identity.profile.key, key)
                self.assertTrue(identity.recognized)

    def test_unknown_pairing_is_not_silently_accepted(self):
        identity = StoveIdentity(0, 7, 2, 0x72, 0, 0)
        self.assertIsNone(select_profile(identity))
        self.assertFalse(identity.recognized)

    def test_profiles_publish_capabilities_and_register_meanings(self):
        profile = PROFILES_BY_KEY["fw202-format04"]
        self.assertEqual(
            profile.capabilities.state(Capability.MONITOR),
            CapabilityState.AVAILABLE,
        )
        self.assertEqual(
            profile.capabilities.state(Capability.FIRMWARE_LOADER),
            CapabilityState.PLANNED,
        )
        self.assertEqual(profile.controller_registers[0x02].name, "physical_inputs")
        self.assertEqual(profile.controller_writes[0x0E].name, "remote_front_panel")
        self.assertFalse(
            profile.controller_writes[0x0E].same_address_readback_meaningful
        )

    def test_data_format_fallback_is_decode_only(self):
        self.assertEqual(profile_for_data_format(7).key, "fw271-format07")
        self.assertIsNone(profile_for_data_format(6))
        self.assertEqual(len(PROFILES), 4)


if __name__ == "__main__":
    unittest.main()
