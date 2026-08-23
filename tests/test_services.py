import unittest

from openmaxfire.checkout import CheckoutOutcome
from openmaxfire.configuration import plan_configuration_update
from openmaxfire.control import ControlOutcome
from openmaxfire.errors import (
    CapabilityUnavailableError,
    SafetyInterlockError,
    VerificationError,
)
from openmaxfire.services import (
    ConfigurationExecutionOutcome,
    ReadOnlyCheckoutRunner,
    execute_configuration_plan,
    execute_control,
    execute_simulated_checkout,
)
from openmaxfire.session import ConnectionInfo, ControllerSession
from openmaxfire.simulator import SimulatedController


class ReadOnlyCheckoutRunnerTests(unittest.TestCase):
    def test_verification_tests_share_one_cached_configuration(self):
        with ControllerSession.simulated() as session:
            runner = ReadOnlyCheckoutRunner(session)
            results = runner.run_tests((1, 2, 3))
            report = runner.report(results)
            requests = session.client.transport.controller.requests
        self.assertEqual([result.outcome for result in results], [CheckoutOutcome.PASS] * 3)
        self.assertEqual(report.profile_key, "fw271-format07")
        self.assertTrue(report.configuration_backup_sha256)
        self.assertFalse(report.to_dict()["complete"])
        self.assertEqual(len(report.to_dict()["results"]), 3)
        self.assertEqual(sum(r.unit == "A" and r.opcode == "R" for r in requests), 256)

    def test_passive_input_poll_uses_machine_predicate_only(self):
        controller = SimulatedController(
            "fw202-format04", controller_registers={0x02: 0x20}
        )
        with ControllerSession.simulated(controller=controller) as session:
            result = ReadOnlyCheckoutRunner(session).run_test(11)
        self.assertEqual(result.outcome, CheckoutOutcome.PASS)
        self.assertEqual(result.observations["CR02"], "20")

    def test_actuator_and_manual_tests_are_never_fabricated(self):
        with ControllerSession.simulated() as session:
            runner = ReadOnlyCheckoutRunner(session)
            actuator = runner.run_test(20)
            manual = runner.run_test(25)
        self.assertEqual(actuator.outcome, CheckoutOutcome.NOT_RUN)
        self.assertEqual(manual.outcome, CheckoutOutcome.NOT_RUN)


class SimulatedWorkflowTests(unittest.TestCase):
    def test_configuration_apply_requires_authorization_and_verifies_all_bytes(self):
        with ControllerSession.simulated(allow_writes=True) as session:
            current = session.read_configuration_image()
            plan = plan_configuration_update(
                current, {"fuel_a.fan.level_1": 0x42}, session.profile
            )
            with self.assertRaises(PermissionError):
                execute_configuration_plan(session, plan)
            result = execute_configuration_plan(session, plan, authorize=True)
        self.assertEqual(result.outcome, ConfigurationExecutionOutcome.VERIFIED)
        self.assertEqual(result.observed.raw[0x40], 0x42)
        self.assertTrue(result.observed.checksum_valid)

    def test_stale_configuration_plan_is_rejected_before_writes(self):
        with ControllerSession.simulated(allow_writes=True) as session:
            current = session.read_configuration_image()
            plan = plan_configuration_update(
                current, {"fuel_a.fan.level_1": 0x42}, session.profile
            )
            session.client.write_register_verified(0x41, 0x55, unit="A")
            with self.assertRaises(VerificationError):
                execute_configuration_plan(session, plan, authorize=True)

    def test_physical_configuration_execution_stays_blocked(self):
        session = ControllerSession.simulated(allow_writes=True)
        current = session.read_configuration_image()
        plan = plan_configuration_update(
            current, {"fuel_a.fan.level_1": 0x42}, session.profile
        )
        session.connection = ConnectionInfo("COM1", 19200, 0.35, False)
        try:
            with self.assertRaises(CapabilityUnavailableError):
                execute_configuration_plan(session, plan, authorize=True)
        finally:
            session.close()

    def test_control_executor_verifies_level_and_off_transitions(self):
        with ControllerSession.simulated(allow_writes=True) as session:
            up = execute_control(
                session, "up", authorize=True, minimum_interval=0
            )
            off = execute_control(
                session, "off", authorize=True, minimum_interval=0
            )
        self.assertEqual(up.outcome, ControlOutcome.VERIFIED)
        self.assertEqual(up.after.target_heat_level, 5)
        self.assertEqual(off.outcome, ControlOutcome.VERIFIED)
        self.assertEqual(off.after.operating_state.phase, "off")
        self.assertEqual(off.to_dict()["outcome"], "verified")

    def test_open_door_blocks_non_off_control(self):
        controller = SimulatedController(
            "fw271-format07", allow_writes=True, controller_registers={0x02: 0x20}
        )
        with ControllerSession.simulated(controller=controller) as session:
            with self.assertRaises(SafetyInterlockError):
                execute_control(session, "up", authorize=True, minimum_interval=0)

    def test_checkout_cleanup_runs_when_observer_raises(self):
        controller = SimulatedController("fw271-format07", allow_writes=True)

        def broken_observer(number):
            raise RuntimeError("observer failed")

        with ControllerSession.simulated(controller=controller) as session:
            result = execute_simulated_checkout(
                session, 20, authorize=True, observation_provider=broken_observer
            )
        self.assertEqual(result.outcome, CheckoutOutcome.INDETERMINATE)
        self.assertEqual(controller.registers[("C", 0x08)], 0)
        self.assertEqual(result.observations["cleanup_requests"], ["435730383030"])

    def test_checkout_without_proven_cleanup_stays_blocked(self):
        with ControllerSession.simulated(allow_writes=True) as session:
            with self.assertRaises(SafetyInterlockError):
                execute_simulated_checkout(session, 15, authorize=True)


if __name__ == "__main__":
    unittest.main()
