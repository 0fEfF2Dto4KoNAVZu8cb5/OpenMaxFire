import unittest

from openmaxfire.session import ControllerSession
from openmaxfire.simulator import SimulatedTransportFactory


class ControllerSessionTests(unittest.TestCase):
    def test_auto_detection_opens_exact_profile_session(self):
        factory = SimulatedTransportFactory("fw202-format04")
        session = ControllerSession.connect(
            "SIM0", timeout=0.01, request_delay=0, transport_factory=factory
        )
        try:
            self.assertEqual(session.profile.key, "fw202-format04")
            self.assertEqual(session.connection.baudrate, 9600)
            self.assertTrue(session.simulated_backend)
            self.assertGreaterEqual(len(factory.transports), 2)
        finally:
            session.close()
        self.assertTrue(session.closed)

    def test_poll_snapshot_ingests_interleaved_simulated_telemetry(self):
        with ControllerSession.simulated("fw271-format07") as session:
            snapshot = session.poll_snapshot()
        self.assertTrue(snapshot.fresh)
        self.assertEqual(snapshot.profile_key, "fw271-format07")
        self.assertEqual(snapshot.operating_state.phase, "operating")
        self.assertEqual(snapshot.target_heat_level, 4)

    def test_snapshot_iterator_is_bounded_and_reuses_state(self):
        with ControllerSession.simulated() as session:
            snapshots = list(session.iter_snapshots(cycles=2, interval=0))
        self.assertEqual(len(snapshots), 2)
        self.assertTrue(all(snapshot.fresh for snapshot in snapshots))
        with ControllerSession.simulated() as session:
            with self.assertRaises(ValueError):
                list(session.iter_snapshots(cycles=1.5, interval=0))

    def test_configuration_image_and_document_are_lossless(self):
        with ControllerSession.simulated("fw206-format05") as session:
            image = session.read_configuration_image()
            document = session.configuration_backup_document()
        self.assertTrue(image.checksum_valid)
        self.assertEqual(document["raw_hex"], image.raw.hex().upper())
        self.assertEqual(document["controller_identity"]["profile_key"], "fw206-format05")


if __name__ == "__main__":
    unittest.main()
