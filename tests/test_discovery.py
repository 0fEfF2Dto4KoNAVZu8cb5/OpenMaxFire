import unittest

from openmaxfire.discovery import DetectionStatus, detect_controller, detect_controllers
from openmaxfire.simulator import SimulatedController, SimulatedTransport, SimulatedTransportFactory


class DiscoveryTests(unittest.TestCase):
    def test_detects_live_profile_at_9600_using_reads_only(self):
        factory = SimulatedTransportFactory("fw202-format04")
        result = detect_controller("SIM0", request_delay=0, transport_factory=factory)
        self.assertEqual(result.status, DetectionStatus.DETECTED)
        self.assertEqual(result.baudrate, 9600)
        self.assertEqual(result.profile.key, "fw202-format04")
        self.assertEqual(
            factory.transports[0].writes,
            [b"CR00", b"CR08", b"CR0B", b"CR0C", b"CR0D", b"CR0E"],
        )
        self.assertTrue(factory.transports[0].closed)

    def test_tries_second_baud_after_read_timeout(self):
        factory = SimulatedTransportFactory("fw271-format07")
        result = detect_controller("SIM0", request_delay=0, transport_factory=factory)
        self.assertEqual(result.status, DetectionStatus.DETECTED)
        self.assertEqual(result.baudrate, 19200)
        self.assertEqual([item.baudrate for item in result.attempts], [9600, 19200])
        self.assertFalse(result.attempts[0].responded)

    def test_valid_unknown_identity_returns_unsupported(self):
        controller = SimulatedController(
            "fw202-format04", controller_registers={0x0C: 0x99}
        )

        def factory(_settings):
            return SimulatedTransport(controller)

        result = detect_controller(
            "SIM0", baudrates=(9600,), request_delay=0, transport_factory=factory
        )
        self.assertEqual(result.status, DetectionStatus.UNSUPPORTED)
        self.assertIsNotNone(result.identity)
        self.assertIsNone(result.profile)

    def test_discovery_report_preserves_no_response(self):
        factory = SimulatedTransportFactory("fw202-format04", port="OTHER")
        report = detect_controllers(
            ["SIM0"], request_delay=0, transport_factory=factory
        )
        self.assertEqual(report.results[0].status, DetectionStatus.NO_RESPONSE)
        self.assertEqual(report.detected, ())


if __name__ == "__main__":
    unittest.main()
