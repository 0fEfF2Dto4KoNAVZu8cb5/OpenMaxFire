import unittest

from openmaxfire.checkout import (
    CHECKOUT_TESTS,
    CheckoutOutcome,
    checkout_test,
    plan_checkout_test,
)
from openmaxfire.profiles import PROFILES_BY_KEY


class CheckoutCatalogTests(unittest.TestCase):
    def test_catalog_contains_exactly_reachable_tests_1_through_45(self):
        self.assertEqual([test.number for test in CHECKOUT_TESTS], list(range(1, 46)))
        self.assertEqual(checkout_test(45).key, "feed_motor_sensor")
        with self.assertRaises(ValueError):
            checkout_test(46)

    def test_passive_predicates_are_machine_evaluable(self):
        door_open = checkout_test(11)
        self.assertEqual(
            door_open.evaluate({("C", 0x02): 0x20}), CheckoutOutcome.PASS
        )
        self.assertEqual(
            door_open.evaluate({("C", 0x02): 0x00}), CheckoutOutcome.FAIL
        )
        self.assertEqual(door_open.evaluate({}), CheckoutOutcome.INDETERMINATE)

    def test_convection_command_is_profile_specific(self):
        old = plan_checkout_test(20, PROFILES_BY_KEY["fw206-format05"])
        new = plan_checkout_test(20, PROFILES_BY_KEY["fw271-format07"])
        self.assertEqual(old.operations[0].value, 0x01)
        self.assertEqual(new.operations[0].value, 0x19)
        self.assertEqual(new.cleanup[0].value, 0)

    def test_actuator_plans_remain_blocked(self):
        plan = plan_checkout_test(38, PROFILES_BY_KEY["fw271-format07"])
        self.assertFalse(plan.executable)
        self.assertIn("planned", " ".join(plan.blockers))

    def test_unreconstructed_or_uncleanable_actions_have_explicit_blockers(self):
        plan = plan_checkout_test(41, PROFILES_BY_KEY["fw271-format07"])
        self.assertFalse(plan.executable)
        self.assertIn("complete action sequence", " ".join(plan.blockers))
        self.assertIn("cleanup", " ".join(plan.blockers))


if __name__ == "__main__":
    unittest.main()
