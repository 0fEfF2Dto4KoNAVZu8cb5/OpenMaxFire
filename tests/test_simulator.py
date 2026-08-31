import unittest

from openmaxfire.client import MaxFireClient
from openmaxfire.protocol import RemoteButton
from openmaxfire.simulator import SimulatedController, SimulatedTransport


class SimulatorTests(unittest.TestCase):
    def test_simulator_implements_client_transport_contract(self):
        transport = SimulatedTransport(SimulatedController("fw206-format05"))
        identity = MaxFireClient(transport).identify()
        self.assertEqual(identity.profile.key, "fw206-format05")

    def test_writes_are_blocked_by_default(self):
        controller = SimulatedController("fw271-format07")
        transport = SimulatedTransport(controller)
        client = MaxFireClient(transport)
        client.write_register(0x40, 0x55, unit="A")
        self.assertNotEqual(controller.registers[("A", 0x40)], 0x55)

    def test_enabled_write_can_be_freshly_read_back(self):
        controller = SimulatedController("fw271-format07", allow_writes=True)
        receipt = MaxFireClient(SimulatedTransport(controller)).write_register_verified(
            0x40, 0x55, unit="A"
        )
        self.assertTrue(receipt.verified)
        self.assertEqual(controller.registers[("A", 0x40)], 0x55)

    def test_faults_can_drop_specific_reads(self):
        controller = SimulatedController("fw271-format07")
        controller.faults.drop_reads.add(("C", 0x08))
        with self.assertRaises(TimeoutError):
            MaxFireClient(SimulatedTransport(controller)).query_register(0x08)

    def test_format04_remote_control_changes_t0c_not_t09(self):
        controller = SimulatedController("fw202-format04", allow_writes=True)
        client = MaxFireClient(SimulatedTransport(controller))
        client.remote_button(RemoteButton.ON)
        self.assertEqual(controller.telemetry[0x0C], 0x30)
        self.assertEqual(controller.telemetry[0x09], 0x07)
        client.remote_button(RemoteButton.OFF)
        self.assertEqual(controller.telemetry[0x0C], 0x20)


if __name__ == "__main__":
    unittest.main()
