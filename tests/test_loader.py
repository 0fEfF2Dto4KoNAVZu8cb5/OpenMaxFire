import unittest

from openmaxfire.audit import AuditTrail
from openmaxfire.errors import CapabilityUnavailableError
from openmaxfire.firmware import FirmwareImage
from openmaxfire.loader import (
    LoaderAttemptOutcome,
    LoaderPolicy,
    LoaderState,
    build_loader_plan,
    execute_loader_plan,
    live_loader_supported,
    loader_simulation_supported,
)
from openmaxfire.profiles import PROFILES_BY_KEY
from openmaxfire.simulator import SimulatedLoaderFaults, SimulatedLoaderTransport


def record(address, record_type, payload=b""):
    body = bytes(
        [len(payload), (address >> 8) & 0xFF, address & 0xFF, record_type]
    ) + payload
    return ":" + (body + bytes([(-sum(body)) & 0xFF])).hex().upper()


def image(name="Bixby_0271_080315.hex"):
    source = "\n".join(
        (
            record(0, 0, bytes(range(40))),
            record(0x400E, 0, b"\x72\x3F"),
            record(0, 1),
        )
    )
    return FirmwareImage.parse(source, filename=name)


class LoaderStateMachineTests(unittest.TestCase):
    def test_complete_simulation_frames_blocks_and_verifies_memory(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        transport = SimulatedLoaderTransport()
        audit = AuditTrail(session_id="loader-test")
        result = execute_loader_plan(
            transport, plan, authorize=True, audit=audit
        )
        self.assertEqual(result.state, LoaderState.COMPLETE)
        self.assertTrue(result.successful)
        self.assertEqual(result.blocks_total, 2)
        self.assertEqual(result.blocks_completed, 2)
        self.assertEqual(transport.writes[0], b"\xEA")
        self.assertEqual(transport.writes[-1], b"\xED")
        self.assertTrue(result.pic_side_blocks_verified)
        self.assertTrue(result.application_handoff)
        self.assertTrue(result.application_reconnected)
        self.assertGreater(result.audit_span.event_count, 0)

    def test_e8_and_e5_are_classified_then_retried(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        faults = SimulatedLoaderFaults(
            identify_failures=1,
            checksum_failures={0: 1},
            write_failures={0: 1},
        )
        result = execute_loader_plan(
            SimulatedLoaderTransport(faults=faults),
            plan,
            authorize=True,
            policy=LoaderPolicy(max_retries=3),
        )
        self.assertTrue(result.successful)
        self.assertEqual(result.retries, 3)
        self.assertEqual(result.block_receipts[0].attempts, 3)
        self.assertEqual(
            [item.outcome for item in result.block_receipts[0].attempt_receipts],
            [
                LoaderAttemptOutcome.CHECKSUM_REJECTED,
                LoaderAttemptOutcome.WRITE_VERIFICATION_FAILED,
                LoaderAttemptOutcome.ACKNOWLEDGED,
            ],
        )

    def test_retry_exhaustion_transmits_terminal_frame_without_accepting_it(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(write_failures={0: 5})
        )
        result = execute_loader_plan(
            transport,
            plan,
            authorize=True,
            policy=LoaderPolicy(max_retries=1),
        )
        self.assertEqual(result.state, LoaderState.FAILED)
        self.assertEqual(result.blocks_completed, 0)
        self.assertEqual(result.block_receipts[0].accepted_attempts, 2)
        self.assertEqual(result.block_receipts[0].transmissions, 3)
        self.assertEqual(
            result.block_receipts[0].attempt_receipts[-1].outcome,
            LoaderAttemptOutcome.TERMINAL_TRANSMISSION_UNREAD,
        )
        self.assertEqual(transport.incoming, b"\xE7\xE5")

    def test_default_policy_matches_thirty_accepted_attempts(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        result = execute_loader_plan(
            SimulatedLoaderTransport(
                faults=SimulatedLoaderFaults(write_failures={0: 100})
            ),
            plan,
            authorize=True,
        )
        receipt = result.block_receipts[0]
        self.assertEqual(receipt.accepted_attempts, 30)
        self.assertEqual(receipt.transmissions, 31)
        self.assertEqual(result.retries, 29)

    def test_corrupt_simulated_memory_cannot_report_success(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        result = execute_loader_plan(
            SimulatedLoaderTransport(
                faults=SimulatedLoaderFaults(corrupt_word_address=0x1E85)
            ),
            plan,
            authorize=True,
        )
        self.assertEqual(result.state, LoaderState.FAILED)
        self.assertFalse(result.memory_verified)

    def test_partial_row_preserves_neighbors_and_retries_internally(self):
        source = "\n".join(
            (
                record(0x000A, 0, b"\x34\x12"),
                record(0x400E, 0, b"\x72\x3F"),
                record(0, 1),
            )
        )
        plan = build_loader_plan(
            FirmwareImage.parse(source, filename="Bixby_0271_080315.hex"),
            PROFILES_BY_KEY["fw271-format07"],
        )
        transport = SimulatedLoaderTransport(
            initial_program_words={4: 0x1111, 5: 0x2222, 6: 0x3333, 7: 0x0444},
            faults=SimulatedLoaderFaults(row_write_failures={4: 1}),
        )
        result = execute_loader_plan(transport, plan, authorize=True)
        self.assertTrue(result.successful)
        self.assertEqual(
            {address: transport.flash_words[address] for address in range(4, 8)},
            {4: 0x1111, 5: 0x1234, 6: 0x3333, 7: 0x0444},
        )
        self.assertEqual(transport.row_write_attempts[4], 2)
        self.assertTrue(transport.preserved_neighbors_verified)

    def test_reset_words_relocate_and_direct_loader_targets_are_skipped(self):
        low_words = b"\x01\x10\x02\x10\x03\x10\x04\x10"
        protected_words = b"\x10\x20\x11\x20\x12\x20\x13\x20"
        source = "\n".join(
            (
                record(0x0000, 0, low_words),
                record(0x3D00, 0, protected_words),
                record(0x400E, 0, b"\x72\x3F"),
                record(0, 1),
            )
        )
        plan = build_loader_plan(
            FirmwareImage.parse(source, filename="Bixby_0271_080315.hex"),
            PROFILES_BY_KEY["fw271-format07"],
        )
        initial = {0x1E80 + offset: 0x3000 + offset for offset in range(8)}
        transport = SimulatedLoaderTransport(initial_program_words=initial)
        result = execute_loader_plan(transport, plan, authorize=True)
        self.assertTrue(result.successful)
        self.assertEqual(plan.relocated_word_count, 4)
        self.assertEqual(plan.protected_skipped_word_count, 4)
        self.assertEqual(transport.flash_words[0x1E80], 0x3000)
        self.assertEqual(
            [transport.flash_words[0x1E84 + offset] for offset in range(4)],
            [0x1001, 0x1002, 0x1003, 0x1004],
        )

    def test_completion_is_not_retried_and_reconnect_fails_closed(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        completion = execute_loader_plan(
            SimulatedLoaderTransport(
                faults=SimulatedLoaderFaults(completion_failures=1)
            ),
            plan,
            authorize=True,
        )
        self.assertEqual(completion.state, LoaderState.FAILED)
        self.assertIn("does not resend ED", completion.message)

        reconnect = execute_loader_plan(
            SimulatedLoaderTransport(
                faults=SimulatedLoaderFaults(reconnect_failures=1)
            ),
            plan,
            authorize=True,
        )
        self.assertEqual(reconnect.state, LoaderState.FAILED)
        self.assertTrue(reconnect.memory_verified)
        self.assertTrue(reconnect.application_handoff)
        self.assertFalse(reconnect.application_reconnected)

    def test_pickit_plan_is_blocked_and_live_transport_is_rejected(self):
        plan = build_loader_plan(
            image("Bixby_02060021_PICkit.hex"),
            PROFILES_BY_KEY["fw202-format04"],
        )
        blocked = execute_loader_plan(
            SimulatedLoaderTransport(), plan, authorize=True
        )
        self.assertEqual(blocked.state, LoaderState.BLOCKED)

        class FakePhysicalTransport:
            def write(self, data): pass
            def read(self, size=1): return b""
            def close(self): pass

        with self.assertRaises(CapabilityUnavailableError):
            execute_loader_plan(FakePhysicalTransport(), plan, authorize=True)
        self.assertTrue(loader_simulation_supported())
        self.assertTrue(live_loader_supported())

    def test_authorization_is_mandatory_even_for_simulation(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        with self.assertRaises(PermissionError):
            execute_loader_plan(SimulatedLoaderTransport(), plan)


if __name__ == "__main__":
    unittest.main()
