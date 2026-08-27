import unittest

from openmaxfire.control import ControlAction, plan_control
from openmaxfire.models import AlarmState, StoveSnapshot, TelemetryMeasurements
from openmaxfire.profiles import PROFILES_BY_KEY
from openmaxfire.protocol import OperatingState


def snapshot(level=4, *, fresh=True, phase="operating"):
    state = OperatingState(0x43, 0x43, 4, phase, "Level 4", level=level)
    return StoveSnapshot(
        profile_key="fw271-format07",
        firmware_version="2.71",
        data_format=7,
        fresh=fresh,
        age_seconds=0.1,
        observed_utc=None,
        panel_buttons=None,
        physical_inputs=None,
        thermostat_open=False,
        alarms=AlarmState(),
        operating_state=state,
        format04_state_candidate=None,
        igniter_state=None,
        current_heat_level=level,
        target_heat_level=level,
        telemetry=TelemetryMeasurements(),
        controller_registers={},
        telemetry_bytes={},
        status_payloads={},
        evidence="fixture",
    )


class ControlPlanningTests(unittest.TestCase):
    def test_set_level_builds_bounded_button_sequence(self):
        plan = plan_control(
            ControlAction.SET_LEVEL,
            PROFILES_BY_KEY["fw271-format07"],
            snapshot(),
            target_level=6,
        )
        self.assertEqual([operation.value for operation in plan.operations], [0x14, 0x14])
        self.assertFalse(plan.executable)

    def test_set_level_is_idempotent(self):
        plan = plan_control(
            "set_level",
            PROFILES_BY_KEY["fw271-format07"],
            snapshot(),
            target_level=4,
        )
        self.assertTrue(plan.already_satisfied)
        self.assertEqual(plan.operations, ())
        self.assertTrue(plan.executable)

    def test_stale_snapshot_blocks_state_change(self):
        plan = plan_control(
            "up", PROFILES_BY_KEY["fw271-format07"], snapshot(fresh=False)
        )
        self.assertFalse(plan.executable)
        self.assertIn("stale", " ".join(plan.blockers))

    def test_on_is_already_satisfied_during_each_startup_phase(self):
        for phase in ("prefill", "started", "starting", "ignited"):
            with self.subTest(phase=phase):
                plan = plan_control(
                    "on", PROFILES_BY_KEY["fw271-format07"], snapshot(phase=phase)
                )
                self.assertTrue(plan.already_satisfied)
                self.assertEqual(plan.operations, ())


if __name__ == "__main__":
    unittest.main()
