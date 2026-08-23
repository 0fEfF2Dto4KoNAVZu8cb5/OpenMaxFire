import unittest

from openmaxfire.audit import AuditTrail
from openmaxfire.errors import CapabilityUnavailableError
from openmaxfire.firmware import FirmwareImage
from openmaxfire.loader import (
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
        self.assertGreater(result.audit_span.event_count, 0)

    def test_transient_identify_and_block_faults_are_retried(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        faults = SimulatedLoaderFaults(
            identify_failures=1,
            block_failures={0: 2},
            completion_failures=1,
        )
        result = execute_loader_plan(
            SimulatedLoaderTransport(faults=faults),
            plan,
            authorize=True,
            policy=LoaderPolicy(max_retries=3),
        )
        self.assertTrue(result.successful)
        self.assertEqual(result.retries, 4)
        self.assertEqual(result.block_receipts[0].attempts, 3)

    def test_retry_exhaustion_returns_partial_failure_receipt(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        result = execute_loader_plan(
            SimulatedLoaderTransport(
                faults=SimulatedLoaderFaults(block_failures={0: 5})
            ),
            plan,
            authorize=True,
            policy=LoaderPolicy(max_retries=1),
        )
        self.assertEqual(result.state, LoaderState.FAILED)
        self.assertEqual(result.blocks_completed, 0)
        self.assertEqual(result.block_receipts[0].attempts, 2)

    def test_corrupt_simulated_memory_cannot_report_success(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        result = execute_loader_plan(
            SimulatedLoaderTransport(
                faults=SimulatedLoaderFaults(corrupt_word_address=1)
            ),
            plan,
            authorize=True,
        )
        self.assertEqual(result.state, LoaderState.FAILED)
        self.assertFalse(result.memory_verified)

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
        self.assertFalse(live_loader_supported())

    def test_authorization_is_mandatory_even_for_simulation(self):
        plan = build_loader_plan(image(), PROFILES_BY_KEY["fw271-format07"])
        with self.assertRaises(PermissionError):
            execute_loader_plan(SimulatedLoaderTransport(), plan)


if __name__ == "__main__":
    unittest.main()
