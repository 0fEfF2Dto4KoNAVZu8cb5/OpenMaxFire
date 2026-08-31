import contextlib
import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from openmaxfire.client import MaxFireClient
from openmaxfire.backup import save_json_document
from openmaxfire.errors import SafetyInterlockError, UnsupportedControllerError, VerificationError
from openmaxfire.firmware import FirmwareImage
from openmaxfire.flashing import (
    LOADER_BAUDRATE,
    LOADER_BOOT_WINDOW_ESTIMATE_SECONDS,
    FlashJournal,
    FlashSessionState,
    FlashSessionStatus,
    FlashSafetyInterlocks,
    LiveLoaderPolicy,
    approve_live_firmware,
    execute_loader_rehearsal,
    execute_live_loader_plan,
    delegate_recovery_source,
    load_recovery_bundle,
    prepare_live_flash,
    prepare_recovery_flash,
    preserve_recovery_bundle,
    qualify_flash_preparation,
    recover_live_loader_completion,
    wait_for_application_ready,
    verify_post_flash,
    validate_live_transition,
)
from openmaxfire.loader import LoaderAttemptOutcome
from openmaxfire.simulator import (
    SimulatedController,
    SimulatedFlashSessionTransport,
    SimulatedLoaderFaults,
    SimulatedLoaderTransport,
    SimulatedTransport,
    default_eeprom,
)
from openmaxfire.profiles import PROFILES_BY_KEY


ROOT = Path(__file__).resolve().parents[1]
FW206 = ROOT / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex"
FW206_PICKIT = ROOT / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex"
FW270 = ROOT / "reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex"


def safe_interlocks(**overrides):
    values = {
        "stove_cold_and_off": True,
        "igniters_physically_unplugged": True,
        "actuator_loads_physically_unplugged": True,
        "correct_5v_ttl_wiring": True,
        "j3_pin3_disconnected": True,
        "adapter_vcc_disconnected": True,
        "pickit_recovery_tested_on_spare": True,
        "computer_power_stable": True,
        "stove_power_stable": True,
        "calibration_plan_ready": True,
        "downgrade_stale_flash_accepted": False,
    }
    values.update(overrides)
    return FlashSafetyInterlocks(**values)


class FakeSleepInhibitor:
    backend = "test.sleep-inhibitor"

    def __enter__(self):
        return self

    def ensure_active(self):
        return None

    def __exit__(self, exc_type, exc, traceback):
        return None


class LiveFlashingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = FirmwareImage.load(FW206)
        cls.safety = safe_interlocks()
        client = MaxFireClient(
            SimulatedTransport(SimulatedController("fw202-format04"))
        )
        try:
            cls.preparation = prepare_live_flash(
                client,
                cls.image,
                port="SIM0",
                current_baudrate=9600,
                interlocks=cls.safety,
                request_delay=0,
            )
        finally:
            client.close()

    def test_only_exact_authenticated_downloader_images_are_approved(self):
        approved = approve_live_firmware(self.image)
        self.assertEqual(approved.target_profile_key, "fw206-format05")
        self.assertEqual(approved.application_baudrate, 9600)
        with self.assertRaises(VerificationError):
            approve_live_firmware(FirmwareImage.load(FW206_PICKIT))

        tiny = b":020000000000FE\n:00000001FF\n"
        with self.assertRaises(UnsupportedControllerError) as raised:
            approve_live_firmware(
                FirmwareImage.parse(tiny, filename="Bixby_0273_Downloader.hex")
            )
        self.assertIn("contact@openmaxfire.com", str(raised.exception))

    def test_forward_upgrades_cannot_skip_preserved_vendor_generations(self):
        validate_live_transition("2.02", "2.06")
        validate_live_transition("2.06", "2.70")
        validate_live_transition("2.70", "2.71")
        with self.assertRaises(VerificationError):
            validate_live_transition("2.71", "2.06")
        with self.assertRaises(VerificationError):
            validate_live_transition("2.06", "2.06")
        with self.assertRaises(VerificationError):
            validate_live_transition("2.02", "2.70")
        with self.assertRaises(VerificationError):
            validate_live_transition("2.06", "2.71")

    def test_preflight_requires_exact_identity_backup_and_human_interlocks(self):
        client = MaxFireClient(
            SimulatedTransport(SimulatedController("fw202-format04"))
        )
        try:
            with self.assertRaises(SafetyInterlockError) as raised:
                prepare_live_flash(
                    client,
                    self.image,
                    port="SIM0",
                    current_baudrate=9600,
                    interlocks=FlashSafetyInterlocks(),
                    request_delay=0,
                )
        finally:
            client.close()
        self.assertIn("igniters", str(raised.exception))
        self.assertIn("hazardous actuator loads", str(raised.exception))
        self.assertIn("spare PIC", str(raised.exception))

    def test_complete_live_protocol_uses_9600_and_pic_side_verification(self):
        transport = SimulatedLoaderTransport()
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertTrue(result.successful)
        self.assertTrue(result.pic_side_blocks_verified)
        self.assertEqual(result.blocks_completed, result.blocks_total)
        self.assertEqual(transport.writes[0], b"\xEA")
        self.assertEqual(transport.writes[-1], b"\xED")
        self.assertTrue(transport.application_running)

    def test_live_protocol_settles_after_identify_before_first_program_frame(self):
        transport = SimulatedLoaderTransport()
        with mock.patch("openmaxfire.flashing.time.sleep") as sleep:
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(
                    retry_delay=0,
                    post_identify_settle_delay=2.0,
                    response_timeout=2.0,
                ),
            )
        self.assertTrue(result.successful)
        sleep.assert_any_call(2.0)
        self.assertEqual(transport.writes[0], b"\xEA")
        self.assertEqual(transport.writes[1][0], 0xE3)

    def test_live_loader_policy_rejects_invalid_settle_delay(self):
        for value in (-0.01, 5.01, float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    LiveLoaderPolicy(post_identify_settle_delay=value)

    def test_live_loader_policy_bounds_probe_timeout(self):
        self.assertEqual(LiveLoaderPolicy(probe_timeout=0.005).probe_timeout, 0.005)
        for value in (0, 0.0009, 0.0501, float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    LiveLoaderPolicy(probe_timeout=value)

    def test_identify_retry_delay_is_independent_and_bounded(self):
        self.assertEqual(LiveLoaderPolicy().identify_retry_delay, 0.0)
        self.assertEqual(
            LiveLoaderPolicy(identify_retry_delay=0.050).identify_retry_delay,
            0.050,
        )
        for value in (-0.001, 0.0501, True, float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    LiveLoaderPolicy(identify_retry_delay=value)

    def test_rehearsal_uses_identify_delay_not_block_retry_delay(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(identify_failures=1)
        )
        with mock.patch("openmaxfire.flashing.time.sleep") as sleep:
            result = execute_loader_rehearsal(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(
                    identify_attempts=2,
                    identify_retry_delay=0.007,
                    retry_delay=0.031,
                ),
            )
        self.assertTrue(result.successful)
        sleep.assert_called_once_with(0.007)

    def test_default_identify_loop_adds_no_retry_sleep(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(identify_failures=1)
        )
        with mock.patch("openmaxfire.flashing.time.sleep") as sleep:
            result = execute_loader_rehearsal(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(identify_attempts=2),
            )
        self.assertTrue(result.successful)
        sleep.assert_not_called()

    def test_non_writing_loader_rehearsal_sends_only_ea_and_ed(self):
        transport = SimulatedLoaderTransport()
        result = execute_loader_rehearsal(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertTrue(result.successful)
        self.assertEqual(transport.writes, [b"\xEA", b"\xED"])
        self.assertEqual(transport.blocks_accepted, 0)
        self.assertTrue(transport.application_running)

    def test_application_readiness_waits_for_passive_periodic_telemetry(self):
        class PassiveTransport:
            def __init__(self):
                self.incoming = bytearray(
                    b"\xE4stale-loader-byte\nCR0000\nT0800\n"
                )
                self.writes = []

            def write(self, data):
                self.writes.append(bytes(data))

            def read(self, size=1):
                if not self.incoming:
                    return b""
                chunk = bytes(self.incoming[:size])
                del self.incoming[:size]
                return chunk

            def close(self):
                return None

        transport = PassiveTransport()
        client = MaxFireClient(transport)
        evidence = wait_for_application_ready(client, timeout=0.1)
        self.assertEqual(evidence.frame_kind, "T")
        self.assertEqual(evidence.raw, b"T0800")
        self.assertEqual(evidence.ignored_frames, 2)
        self.assertEqual(evidence.to_dict()["host_transmissions"], 0)
        self.assertEqual(transport.writes, [])

    def test_application_readiness_timeout_never_transmits(self):
        class SilentTransport:
            def __init__(self):
                self.writes = []

            def write(self, data):
                self.writes.append(bytes(data))

            def read(self, size=1):
                return b""

            def close(self):
                return None

        transport = SilentTransport()
        client = MaxFireClient(transport)
        with self.assertRaisesRegex(
            TimeoutError, "no CR00 or other application request was transmitted"
        ):
            wait_for_application_ready(client, timeout=0.001)
        self.assertEqual(transport.writes, [])
    def test_rehearsal_rejects_simulator_subclass_before_loader_traffic(self):
        class PhysicalLookalike(SimulatedLoaderTransport):
            pass

        transport = PhysicalLookalike()
        with self.assertRaisesRegex(SafetyInterlockError, "physical loader traffic"):
            execute_loader_rehearsal(
                transport,
                self.preparation,
                interlocks=self.safety,
            )
        self.assertEqual(transport.writes, [])

    def test_rehearsal_makes_probe_audit_durable_before_ed(self):
        operations = []

        class OrderingAudit:
            buffered = True

            def record(self, direction, data):
                operations.append(("audit", direction, bytes(data)))

            def sync_durable(self):
                operations.append(("sync",))

        audit = OrderingAudit()
        transport = SimulatedLoaderTransport()
        original_write = transport.write

        def record_wire_write(data):
            operations.append(("wire", bytes(data)))
            original_write(data)

        with mock.patch.object(transport, "write", side_effect=record_wire_write):
            result = execute_loader_rehearsal(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
                audit=audit,
            )

        self.assertTrue(result.successful)
        wire_ea = operations.index(("wire", b"\xEA"))
        audit_ea = operations.index(("audit", "tx", b"\xEA"))
        sync = operations.index(("sync",))
        audit_ed = operations.index(("audit", "tx", b"\xED"))
        wire_ed = operations.index(("wire", b"\xED"))
        self.assertLess(wire_ea, audit_ea)  # EA timestamp follows serial flush.
        self.assertLess(audit_ea, sync)
        self.assertLess(sync, audit_ed)
        self.assertLess(audit_ed, wire_ed)  # ED retains pre-write persistence.
        self.assertFalse(audit.buffered)

    def test_live_flash_makes_probe_audit_durable_before_first_e3(self):
        operations = []

        class OrderingAudit:
            buffered = True

            def record(self, direction, data):
                operations.append(("audit", direction, bytes(data)))

            def sync_durable(self):
                operations.append(("sync",))

        audit = OrderingAudit()
        transport = SimulatedLoaderTransport()
        original_write = transport.write

        def record_wire_write(data):
            operations.append(("wire", bytes(data)))
            original_write(data)

        with mock.patch.object(transport, "write", side_effect=record_wire_write):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
                audit=audit,
            )

        self.assertTrue(result.successful)
        sync = operations.index(("sync",))
        audit_e3 = next(
            index
            for index, operation in enumerate(operations)
            if operation[0:2] == ("audit", "tx") and operation[2][0] == 0xE3
        )
        wire_e3 = next(
            index
            for index, operation in enumerate(operations)
            if operation[0] == "wire" and operation[1][0] == 0xE3
        )
        self.assertLess(sync, audit_e3)
        self.assertLess(audit_e3, wire_e3)
        self.assertFalse(audit.buffered)

    def test_failed_rehearsal_syncs_exhausted_probe_evidence_without_ed(self):
        operations = []

        class OrderingAudit:
            buffered = True

            def record(self, direction, data):
                operations.append(("audit", direction, bytes(data)))

            def sync_durable(self):
                operations.append(("sync",))

        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(identify_failures=2)
        )
        result = execute_loader_rehearsal(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(identify_attempts=2, retry_delay=0),
            audit=OrderingAudit(),
        )

        self.assertFalse(result.successful)
        self.assertEqual(transport.writes, [b"\xEA", b"\xEA"])
        self.assertEqual(operations[-1], ("sync",))

    def test_failed_probe_audit_barrier_blocks_first_e3(self):
        class FailedBarrierAudit:
            buffered = True

            def record(self, _direction, _data):
                return None

            def sync_durable(self):
                raise OSError("simulated fsync failure")

        transport = SimulatedLoaderTransport()
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
            audit=FailedBarrierAudit(),
        )

        self.assertFalse(result.successful)
        self.assertEqual(transport.writes, [b"\xEA"])
        self.assertIn("could not be made durable", result.message)
        self.assertTrue(
            any("fsync failure" in error for error in result.diagnostic_errors)
        )

    def test_probe_miss_journal_is_deferred_until_after_timing_barrier(self):
        operations = []

        class OrderingAudit:
            buffered = True

            def record(self, direction, data):
                operations.append(("audit", direction, bytes(data)))

            def sync_durable(self):
                operations.append(("sync",))

        class OrderingJournal:
            def record(self, event, **_fields):
                operations.append(("journal", event))

        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(identify_failures=1)
        )
        original_write = transport.write

        def record_wire_write(data):
            operations.append(("wire", bytes(data)))
            original_write(data)

        with mock.patch.object(transport, "write", side_effect=record_wire_write):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
                audit=OrderingAudit(),
                journal=OrderingJournal(),
            )

        self.assertTrue(result.successful)
        self.assertNotIn(("journal", "loader_probe_miss"), operations)
        sync = operations.index(("sync",))
        misses = operations.index(("journal", "loader_probe_misses"))
        first_e3 = next(
            index
            for index, operation in enumerate(operations)
            if operation[0] == "wire" and operation[1][0] == 0xE3
        )
        self.assertLess(sync, misses)
        self.assertLess(misses, first_e3)

    def test_exact_plan_passes_mandatory_offline_whole_image_qualification(self):
        result = qualify_flash_preparation(self.preparation)
        self.assertTrue(result.successful)
        self.assertTrue(result.memory_verified)

    def test_e8_and_e5_are_classified_and_bounded(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(
                checksum_failures={0: 1},
                write_failures={0: 1},
            )
        )
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(max_block_transmissions=3, retry_delay=0),
        )
        self.assertTrue(result.successful)
        self.assertEqual(result.write_failure_events, 1)
        self.assertTrue(result.anomalies)
        self.assertEqual(
            [item.outcome for item in result.block_receipts[0].attempt_receipts],
            [
                LoaderAttemptOutcome.CHECKSUM_REJECTED,
                LoaderAttemptOutcome.WRITE_VERIFICATION_FAILED,
                LoaderAttemptOutcome.ACKNOWLEDGED,
            ],
        )

    def test_block_retry_delay_remains_separate_from_identify_pacing(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(checksum_failures={0: 1})
        )
        with mock.patch("openmaxfire.flashing.time.sleep") as sleep:
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(
                    identify_retry_delay=0.0,
                    retry_delay=0.031,
                ),
            )
        self.assertTrue(result.successful)
        sleep.assert_called_once_with(0.031)

    def test_exhaustion_never_transmits_bixcheck_terminal_unread_frame(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(write_failures={0: 99})
        )
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(max_block_transmissions=4, retry_delay=0),
        )
        self.assertFalse(result.successful)
        self.assertEqual(result.blocks_completed, 0)
        self.assertEqual(len(result.block_receipts[0].attempt_receipts), 2)
        self.assertEqual(len(transport.writes), 3)  # EA plus exactly two E3 frames
        self.assertNotIn(b"\xED", transport.writes)

    def test_second_e5_anywhere_in_session_aborts_without_another_retry(self):
        first_address = self.preparation.loader_plan.blocks[0].word_address
        second_address = self.preparation.loader_plan.blocks[1].word_address
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(
                write_failures={first_address: 1, second_address: 1}
            )
        )
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertFalse(result.successful)
        self.assertTrue(result.recovery_required)
        self.assertEqual(result.write_failure_events, 2)
        self.assertEqual(result.blocks_completed, 1)
        self.assertEqual(result.block_receipts[1].attempts, 1)
        self.assertNotIn(b"\xED", transport.writes)

    def test_post_e7_timeout_gets_one_idempotent_retry(self):
        transport = SimulatedLoaderTransport()
        original_program_block = transport._program_block
        dropped = False

        def drop_first_e4(frame):
            nonlocal dropped
            original_program_block(frame)
            if not dropped and transport.incoming.endswith(b"\xE7\xE4"):
                transport.incoming.pop()
                dropped = True

        with mock.patch.object(
            transport, "_program_block", side_effect=drop_first_e4
        ):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertTrue(result.successful)
        outcomes = [
            item.outcome for item in result.block_receipts[0].attempt_receipts
        ]
        self.assertEqual(
            outcomes,
            [
                LoaderAttemptOutcome.POST_ACCEPT_TIMEOUT,
                LoaderAttemptOutcome.ACKNOWLEDGED,
            ],
        )

    def test_delayed_e4_is_accepted_only_after_observed_e7(self):
        transport = SimulatedLoaderTransport()
        original_read = transport.read
        delayed = False

        def delay_first_e4(size=1):
            nonlocal delayed
            if transport.incoming == bytearray(b"\xE4") and not delayed:
                delayed = True
                return b""
            return original_read(size)

        with mock.patch.object(transport, "read", side_effect=delay_first_e4):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertTrue(result.successful)
        self.assertEqual(transport.writes.count(self.preparation.loader_plan.blocks[0].frame), 1)
        self.assertEqual(
            result.block_receipts[0].attempt_receipts[0].outcome,
            LoaderAttemptOutcome.ACKNOWLEDGED,
        )

    def test_stray_late_e4_after_e5_cannot_forge_success(self):
        transport = SimulatedLoaderTransport()
        original_program_block = transport._program_block
        injected = False

        def inject_e5_then_stray_e4(frame):
            nonlocal injected
            if not injected:
                injected = True
                transport.incoming.extend(b"\xE7\xE5\xE4")
                return
            original_program_block(frame)

        with mock.patch.object(
            transport, "_program_block", side_effect=inject_e5_then_stray_e4
        ):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertFalse(result.successful)
        self.assertEqual(result.blocks_completed, 0)
        self.assertEqual(result.failure_outcome, LoaderAttemptOutcome.UNEXPECTED_RESPONSE)
        self.assertEqual(transport.writes.count(self.preparation.loader_plan.blocks[0].frame), 1)

    def test_retry_drain_transport_error_aborts_without_resending(self):
        transport = SimulatedLoaderTransport()
        original_program_block = transport._program_block
        original_read_available = transport.read_available
        awaiting_retry = False

        def drop_until_retry(frame):
            nonlocal awaiting_retry
            if not awaiting_retry:
                awaiting_retry = True
                return
            original_program_block(frame)

        def fail_retry_drain():
            if awaiting_retry:
                raise OSError("simulated in-waiting failure")
            return original_read_available()

        with mock.patch.object(
            transport, "_program_block", side_effect=drop_until_retry
        ), mock.patch.object(
            transport, "read_available", side_effect=fail_retry_drain
        ):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertFalse(result.successful)
        self.assertEqual(result.failure_outcome, LoaderAttemptOutcome.TRANSPORT_ERROR)
        self.assertEqual(transport.writes.count(self.preparation.loader_plan.blocks[0].frame), 1)

    def test_pre_e7_timeout_is_distinct_and_bounded(self):
        transport = SimulatedLoaderTransport()
        original_program_block = transport._program_block
        dropped = False

        def drop_first_frame(frame):
            nonlocal dropped
            if not dropped:
                dropped = True
                return
            original_program_block(frame)

        with mock.patch.object(
            transport, "_program_block", side_effect=drop_first_frame
        ):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertTrue(result.successful)
        self.assertEqual(
            result.block_receipts[0].attempt_receipts[0].outcome,
            LoaderAttemptOutcome.PRE_ACCEPT_TIMEOUT,
        )

    def test_unexpected_byte_aborts_without_blind_retry(self):
        first_address = self.preparation.loader_plan.blocks[0].word_address
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(block_failures={first_address: 1})
        )
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertFalse(result.successful)
        self.assertEqual(result.failure_outcome, LoaderAttemptOutcome.UNEXPECTED_RESPONSE)
        self.assertEqual(result.block_receipts[0].attempts, 1)

    def test_diagnostic_sink_failure_after_first_e3_does_not_interrupt_programming(self):
        class FailedAuditAfterProgrammingStarts:
            buffered = True

            def __init__(self):
                self.e3_intents = 0

            def record(self, direction, data):
                if direction == "tx" and bytes(data).startswith(b"\xE3"):
                    self.e3_intents += 1
                if self.e3_intents > 1:
                    raise OSError("simulated full disk")

            def sync_durable(self):
                if self.e3_intents > 1:
                    raise OSError("simulated full disk")

        class FailedJournal:
            def record(self, *args, **kwargs):
                raise OSError("simulated full disk")

        def broken_progress(*args):
            raise BrokenPipeError("simulated closed output")

        result = execute_live_loader_plan(
            SimulatedLoaderTransport(),
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
            audit=FailedAuditAfterProgrammingStarts(),
            journal=FailedJournal(),
            progress=broken_progress,
        )
        self.assertTrue(result.successful)
        self.assertFalse(result.to_dict()["diagnostics_complete"])
        self.assertTrue(
            any("full disk" in item for item in result.diagnostic_errors)
        )

    def test_non_9600_loader_transport_is_blocked_before_transmission(self):
        transport = SimulatedLoaderTransport()
        transport.settings = SimpleNamespace(baudrate=19200)
        with self.assertRaises(SafetyInterlockError):
            execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertEqual(transport.writes, [])
        self.assertEqual(LOADER_BAUDRATE, 9600)

    def test_entry_uses_timeout_shorter_than_loader_boot_window(self):
        transport = SimulatedLoaderTransport()
        timeouts = []
        transport.set_timeout = timeouts.append
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertTrue(result.successful)
        self.assertEqual(timeouts, [0.020, 0.50])
        self.assertLess(timeouts[0], LOADER_BOOT_WINDOW_ESTIMATE_SECONDS)

    def test_late_buffered_identify_response_is_not_discarded(self):
        transport = SimulatedLoaderTransport()
        original_write = transport.write
        original_read = transport.read
        late_response_pending = False

        def schedule_late_identify(data):
            nonlocal late_response_pending
            if data == b"\xEA" and not transport.identified:
                transport.writes.append(bytes(data))
                transport.identified = True
                late_response_pending = True
                return
            original_write(data)

        def delay_identify(size=1):
            nonlocal late_response_pending
            if late_response_pending:
                late_response_pending = False
                transport.incoming.extend(b"\xEB")
                return b""
            return original_read(size)

        def read_late_available():
            data = bytes(transport.incoming)
            transport.incoming.clear()
            return data

        with mock.patch.object(
            transport, "write", side_effect=schedule_late_identify
        ), mock.patch.object(
            transport, "read", side_effect=delay_identify
        ), mock.patch.object(
            transport, "read_available", side_effect=read_late_available
        ):
            result = execute_live_loader_plan(
                transport,
                self.preparation,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertTrue(result.successful)
        self.assertEqual(transport.writes.count(b"\xEA"), 1)

    def test_failed_checksum_still_preserves_complete_preflight_backup(self):
        raw = bytearray(default_eeprom(PROFILES_BY_KEY["fw202-format04"]))
        raw[0x40] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "eeprom-before.json"
            client = MaxFireClient(
                SimulatedTransport(
                    SimulatedController("fw202-format04", eeprom=raw)
                )
            )
            try:
                with self.assertRaises(VerificationError):
                    prepare_live_flash(
                        client,
                        self.image,
                        port="SIM0",
                        current_baudrate=9600,
                        interlocks=self.safety,
                        request_delay=0,
                        backup_path=path,
                    )
            finally:
                client.close()
            backup = json.loads(path.read_text())
            self.assertFalse(backup["checksum"]["matches"])
            self.assertEqual(len(bytes.fromhex(backup["raw_hex"])), 0x100)

    def test_forged_or_truncated_wire_plan_is_rejected_before_transmission(self):
        forged_plan = replace(
            self.preparation.loader_plan,
            blocks=self.preparation.loader_plan.blocks[:-1],
        )
        forged = replace(self.preparation, loader_plan=forged_plan)
        transport = SimulatedLoaderTransport()
        with self.assertRaises(VerificationError):
            execute_live_loader_plan(
                transport,
                forged,
                interlocks=self.safety,
                policy=LiveLoaderPolicy(retry_delay=0),
            )
        self.assertEqual(transport.writes, [])

    def test_missing_ed_ack_can_recover_only_after_all_blocks_verified(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(completion_failures=1)
        )
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertFalse(result.successful)
        self.assertTrue(result.pic_side_blocks_verified)
        self.assertFalse(result.completion_acknowledged)
        recovered = recover_live_loader_completion(transport, result)
        self.assertTrue(recovered)
        self.assertTrue(transport.application_running)

    def test_completion_recovery_rejects_physical_and_simulator_subclass(self):
        transport = SimulatedLoaderTransport(
            faults=SimulatedLoaderFaults(completion_failures=1)
        )
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )

        class PhysicalTransport:
            simulation_only = True

            def __init__(self):
                self.writes = []

            def write(self, data):
                self.writes.append(bytes(data))

            def read(self, size=1):
                return b""

            def close(self):
                return None

        class SimulatorSubclass(SimulatedLoaderTransport):
            pass

        for candidate in (PhysicalTransport(), SimulatorSubclass()):
            with self.subTest(candidate=type(candidate).__name__):
                with self.assertRaises(SafetyInterlockError):
                    recover_live_loader_completion(candidate, result)
                self.assertEqual(candidate.writes, [])

    def test_postflash_requires_target_identity_and_unchanged_eeprom(self):
        raw = bytes(self.preparation.eeprom_before[address] for address in range(0x100))
        client = MaxFireClient(
            SimulatedTransport(SimulatedController("fw206-format05", eeprom=raw))
        )
        try:
            verification, after, _ = verify_post_flash(
                client, self.preparation, request_delay=0
            )
        finally:
            client.close()
        self.assertEqual(bytes(after.values()), raw)
        self.assertTrue(verification.programming_verified)
        self.assertTrue(verification.calibration_required)
        self.assertFalse(verification.ready_for_operation)

        changed = bytearray(raw)
        changed[0x40] ^= 1
        client = MaxFireClient(
            SimulatedTransport(
                SimulatedController("fw206-format05", eeprom=changed)
            )
        )
        try:
            with self.assertRaises(VerificationError) as raised:
                verify_post_flash(client, self.preparation, request_delay=0)
        finally:
            client.close()
        self.assertIn("A40", str(raised.exception))

    def test_recovery_preparation_uses_prior_backup_without_running_application(self):
        with self.assertRaises(SafetyInterlockError):
            prepare_recovery_flash(
                self.image,
                self.preparation.eeprom_backup,
                port="SIM0",
                current_baudrate=9600,
                interlocks=self.safety,
            )
        recovery_safety = safe_interlocks(recovery_target_matches_backup=True)
        recovery = prepare_recovery_flash(
            self.image,
            self.preparation.eeprom_backup,
            port="SIM0",
            current_baudrate=9600,
            interlocks=recovery_safety,
        )
        self.assertTrue(recovery.recovery_mode)
        transport = SimulatedLoaderTransport()
        result = execute_live_loader_plan(
            transport,
            recovery,
            interlocks=recovery_safety,
            policy=LiveLoaderPolicy(retry_delay=0),
        )
        self.assertTrue(result.successful)

    def test_flash_journal_is_append_only_and_machine_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "journal.jsonl"
            journal = FlashJournal(path, metadata={"image_sha256": self.image.sha256})
            journal.record(
                "block",
                index=1,
                outcome="acknowledged",
                schema="forged-schema",
                sequence=999,
            )
            journal.close()
            events = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([item["event"] for item in events], ["session", "block"])
            self.assertEqual([item["sequence"] for item in events], [1, 2])
            self.assertEqual(
                {item["schema"] for item in events},
                {"openmaxfire.flash-journal.v1"},
            )
            with self.assertRaises(FileExistsError):
                FlashJournal(path, metadata={})

    def test_session_marker_precedes_programming_and_clears_only_when_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            session.mkdir()
            state = FlashSessionState(session, metadata={"image_sha256": self.image.sha256})
            marker = session / "RECOVERY_REQUIRED.txt"
            self.assertFalse(marker.exists())
            state.transition(
                FlashSessionStatus.PROGRAMMING,
                message="armed",
                recovery_required=True,
            )
            self.assertTrue(marker.is_file())
            self.assertIn("block zero", marker.read_text())
            state.transition(
                FlashSessionStatus.COMPLETE,
                message="verified",
                recovery_required=False,
            )
            self.assertFalse(marker.exists())
            document = json.loads((session / "state.json").read_text())
            self.assertEqual(document["status"], "complete_verified")

    def test_recovery_bundle_carries_and_authenticates_exact_hex(self):
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            session.mkdir()
            preparation = self.preparation.to_dict()
            save_json_document(preparation, session / "preparation.json")
            save_json_document(
                self.preparation.eeprom_backup,
                session / "eeprom-before.json",
            )
            preserve_recovery_bundle(
                FW206,
                self.image,
                preparation,
                session_dir=session,
            )
            state = FlashSessionState(
                session, metadata={"image_sha256": self.image.sha256}
            )
            state.transition(
                FlashSessionStatus.RECOVERY_REQUIRED,
                message="simulated interrupted session",
                recovery_required=True,
            )
            image, rebuilt, backup, manifest = load_recovery_bundle(session)
            self.assertEqual(image.sha256, self.image.sha256)
            self.assertEqual(rebuilt["eeprom_before_sha256"], preparation["eeprom_before_sha256"])
            self.assertEqual(backup["raw_hex"], self.preparation.eeprom_backup["raw_hex"])
            self.assertEqual(manifest["firmware_filename"], FW206.name)

            rescue_image = session / "rescue" / FW206.name
            raw = bytearray(rescue_image.read_bytes())
            raw[10] ^= 1
            rescue_image.write_bytes(raw)
            with self.assertRaises(VerificationError):
                load_recovery_bundle(session)

    def test_recovery_bundle_requires_unresolved_marker_and_delegates_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            successor = root / "successor"
            source.mkdir()
            successor.mkdir()
            preparation = self.preparation.to_dict()
            for target in (source, successor):
                save_json_document(preparation, target / "preparation.json")
                save_json_document(
                    self.preparation.eeprom_backup,
                    target / "eeprom-before.json",
                )
                preserve_recovery_bundle(
                    FW206,
                    self.image,
                    preparation,
                    session_dir=target,
                )
            with self.assertRaises(VerificationError):
                load_recovery_bundle(source)

            source_state = FlashSessionState(
                source, metadata={"image_sha256": self.image.sha256}
            )
            source_state.transition(
                FlashSessionStatus.RECOVERY_REQUIRED,
                message="source requires recovery",
                recovery_required=True,
            )
            successor_state = FlashSessionState(
                successor, metadata={"image_sha256": self.image.sha256}
            )
            successor_state.transition(
                FlashSessionStatus.RECOVERY_REQUIRED,
                message="successor owns recovery",
                recovery_required=True,
            )
            delegate_recovery_source(
                source,
                successor,
                image_sha256=self.image.sha256,
            )
            self.assertFalse((source / "RECOVERY_REQUIRED.txt").exists())
            self.assertTrue((source / "RECOVERY_DELEGATED_TO.json").is_file())
            with self.assertRaises(VerificationError) as raised:
                load_recovery_bundle(source)
            self.assertIn(str(successor.resolve()), str(raised.exception))


class FlashCliPlanTests(unittest.TestCase):
    @staticmethod
    def _build_recovery_source(path: Path):
        image = FirmwareImage.load(FW206)
        safety = safe_interlocks()
        client = MaxFireClient(
            SimulatedTransport(SimulatedController("fw202-format04"))
        )
        try:
            preparation = prepare_live_flash(
                client,
                image,
                port="SIM0",
                current_baudrate=9600,
                interlocks=safety,
                request_delay=0,
            )
        finally:
            client.close()
        path.mkdir()
        document = preparation.to_dict()
        save_json_document(document, path / "preparation.json")
        save_json_document(preparation.eeprom_backup, path / "eeprom-before.json")
        preserve_recovery_bundle(FW206, image, document, session_dir=path)
        state = FlashSessionState(path, metadata={"image_sha256": image.sha256})
        state.transition(
            FlashSessionStatus.RECOVERY_REQUIRED,
            message="simulated interrupted source",
            recovery_required=True,
        )
        return preparation

    def test_plan_only_authenticates_image_and_never_opens_serial(self):
        from openmaxfire.cli import main

        output = io.StringIO()
        with mock.patch("openmaxfire.cli.SerialTransport", side_effect=AssertionError):
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "flash",
                        str(FW270),
                        "--plan-only",
                        "--current-profile",
                        "fw206-format05",
                        "--json",
                    ]
                )
        self.assertEqual(result, 0)
        document = json.loads(output.getvalue())
        self.assertEqual(document["schema"], "openmaxfire.live-flash-plan.v2")
        self.assertEqual(document["approved_firmware"]["loader_baudrate"], 9600)
        self.assertEqual(document["approved_firmware"]["application_baudrate"], 19200)
        self.assertTrue(document["data_format_migration_required"])
        self.assertFalse(document["physical_e3_enabled"])
        self.assertEqual(document["execution_mode"], "offline_authenticated_plan")
        self.assertNotIn("manual_power_cycle_required", document)
        self.assertNotIn("software_reset_used", document)
        loader_plan = document["loader_plan"]
        self.assertEqual(loader_plan["schema"], "openmaxfire.loader-plan.v3")
        self.assertTrue(loader_plan["authenticated_simulator_plan"])
        self.assertFalse(loader_plan["physical_e3_enabled"])
        self.assertNotIn("live_executable", loader_plan)
        self.assertIn("hard-disabled", loader_plan["safety_boundary"])

    def test_postwrite_verification_continues_when_traffic_log_cannot_open(self):
        from openmaxfire.cli import _open_recorded_client

        transport = SimulatedFlashSessionTransport(
            "fw202-format04", "fw206-format05"
        )
        errors = []
        args = SimpleNamespace(timeout=0.35, port="SIM0")
        with mock.patch(
            "openmaxfire.cli.JsonlTrafficRecorder",
            side_effect=OSError("simulated full disk"),
        ):
            with contextlib.redirect_stderr(io.StringIO()):
                client = _open_recorded_client(
                    args,
                    transport=transport,
                    baudrate=9600,
                    traffic_path=Path("unused-postflash.jsonl"),
                    phase="postflash-test",
                    diagnostic_errors=errors,
                )
                try:
                    identity = client.identify(request_delay=0)
                finally:
                    client.close()
        self.assertEqual(identity.firmware_version, "2.02")
        self.assertTrue(any("full disk" in item for item in errors))
        self.assertFalse(transport.closed)

    @unittest.skip("retired: public CLI no longer exposes live E3 programming")
    def test_live_cli_runs_preflight_loader_and_postflash_as_separate_phases(self):
        from openmaxfire.cli import main

        raw = default_eeprom(PROFILES_BY_KEY["fw202-format04"])
        transport = SimulatedFlashSessionTransport(
            "fw202-format04", "fw206-format05", eeprom=raw
        )

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "flash-session"
            output = io.StringIO()
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport) as opened:
                with mock.patch(
                    "builtins.input",
                    side_effect=["POWER OFF FOR REHEARSAL", "POWER OFF FOR FLASH"],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(output):
                                result = main(
                                    [
                                        "--port", "SIM0",
                                        "--baud", "9600",
                                        "--request-delay", "0",
                                        "flash", str(FW206),
                                        "--session-dir", str(session),
                                        "--retry-delay", "0",
                                        "--loader-identify-retry-delay", "0.007",
                                        "--loader-probe-timeout", "0.005",
                                        "--confirm-stove-cold-and-off",
                                        "--confirm-igniters-unplugged",
                                        "--confirm-actuator-loads-unplugged",
                                        "--confirm-correct-5v-ttl-wiring",
                                        "--confirm-j3-pin3-disconnected",
                                        "--confirm-adapter-vcc-disconnected",
                                        "--confirm-pickit-recovery-tested-on-spare",
                                        "--confirm-computer-power-stable",
                                        "--confirm-stove-power-stable",
                                        "--confirm-calibration-plan",
                                    ]
                                )
            self.assertEqual(result, 0)
            self.assertEqual(opened.call_count, 1)
            self.assertEqual(transport.loader_entries, 2)
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["successful"])
            self.assertFalse(final["ready_for_operation"])
            self.assertEqual(final["completion_evidence"], "loader_e4")
            self.assertTrue((session / "eeprom-before.json").is_file())
            self.assertTrue((session / "eeprom-after.json").is_file())
            self.assertTrue((session / "loader-traffic.jsonl").is_file())
            self.assertTrue((session / "rehearsal-verification.json").is_file())
            self.assertTrue(
                (session / "rehearsal-application-readiness.json").is_file()
            )
            self.assertTrue((session / "postflash-readiness-1.json").is_file())
            self.assertTrue((session / "offline-qualification.json").is_file())
            self.assertTrue((session / "rescue" / FW206.name).is_file())
            self.assertFalse((session / "RECOVERY_REQUIRED.txt").exists())
            journal = [
                json.loads(line)
                for line in (session / "journal.jsonl").read_text().splitlines()
            ]
            loader_start = next(
                event for event in journal if event.get("event") == "loader_start"
            )
            self.assertEqual(loader_start["probe_timeout"], 0.005)
            self.assertEqual(loader_start["identify_retry_delay"], 0.007)
            rehearsal_start = next(
                event
                for event in journal
                if event.get("event") == "loader_rehearsal_start"
            )
            self.assertEqual(rehearsal_start["identify_retry_delay"], 0.007)

            rehearsal_events = [
                json.loads(line)
                for line in (session / "rehearsal-app-traffic.jsonl")
                .read_text()
                .splitlines()
                if '"event": "traffic"' in line
            ]
            first_tx = next(
                index
                for index, event in enumerate(rehearsal_events)
                if event["direction"] == "tx"
            )
            passive_bytes = b"".join(
                bytes.fromhex(event["data_hex"])
                for event in rehearsal_events[:first_tx]
                if event["direction"] == "rx"
            )
            self.assertIn(b"T0800\n", passive_bytes)
            self.assertEqual(rehearsal_events[first_tx]["data_hex"], "43 52 30 30")

    @unittest.skip("retired: public CLI no longer exposes physical rehearsal")
    def test_rehearsal_can_hold_tx_break_low_during_power_off(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04", "fw206-format05"
        )

        def open_transport(_settings):
            transport.closed = False
            transport.break_active = False
            return transport

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "break-rehearsal"
            with mock.patch(
                "openmaxfire.cli.SerialTransport", side_effect=open_transport
            ):
                with mock.patch(
                    "builtins.input",
                    side_effect=[
                        "POWER OFF FOR REHEARSAL",
                        "AC OFF USB OUT AFTER REHEARSAL",
                        "APPLICATION BOOTED AFTER REHEARSAL",
                        "USB CONNECTED AFTER REHEARSAL",
                    ],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with contextlib.redirect_stdout(io.StringIO()):
                            result = main(
                                [
                                    "--port", "SIM0",
                                    "--baud", "9600",
                                    "--request-delay", "0",
                                    "flash", str(FW206),
                                    "--session-dir", str(session),
                                    "--rehearsal-only",
                                    "--hold-tx-break-during-power-off",
                                    "--retry-delay", "0",
                                    "--confirm-stove-cold-and-off",
                                    "--confirm-igniters-unplugged",
                                    "--confirm-actuator-loads-unplugged",
                                    "--confirm-correct-5v-ttl-wiring",
                                    "--confirm-j3-pin3-disconnected",
                                    "--confirm-adapter-vcc-disconnected",
                                    "--confirm-pickit-recovery-tested-on-spare",
                                    "--confirm-computer-power-stable",
                                    "--confirm-stove-power-stable",
                                    "--confirm-calibration-plan",
                                ]
                            )
            self.assertEqual(result, 0)
            self.assertEqual(
                transport.break_states,
                [True, False, True],
            )
            self.assertEqual(transport.loader_entries, 1)
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["successful"])
            self.assertFalse(final["programming_performed"])
            journal = [
                json.loads(line)
                for line in (session / "journal.jsonl").read_text().splitlines()
            ]
            transitions = [
                event["active"]
                for event in journal
                if event.get("event") == "tx_break_changed"
            ]
            self.assertEqual(transitions, [True, False, True, False])

    @unittest.skip("retired: manual AC/BREAK entry cannot reach E3 from the CLI")
    def test_full_flash_can_guard_every_power_off_with_tx_break(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04", "fw206-format05"
        )

        def open_transport(_settings):
            transport.closed = False
            transport.break_active = False
            return transport

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "guarded-full-flash"
            with mock.patch(
                "openmaxfire.cli.SerialTransport", side_effect=open_transport
            ) as opened:
                with mock.patch(
                    "builtins.input",
                    side_effect=[
                        "POWER OFF FOR REHEARSAL",
                        "AC OFF USB OUT AFTER REHEARSAL",
                        "APPLICATION BOOTED AFTER REHEARSAL",
                        "USB CONNECTED AFTER REHEARSAL",
                        "POWER OFF FOR FLASH",
                        "AC OFF USB OUT AFTER FLASH",
                        "TARGET APPLICATION BOOTED",
                        "USB CONNECTED AFTER FLASH",
                    ],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                result = main(
                                    [
                                        "--port", "SIM0",
                                        "--baud", "9600",
                                        "--request-delay", "0",
                                        "flash", str(FW206),
                                        "--session-dir", str(session),
                                        "--hold-tx-break-during-power-off",
                                        "--retry-delay", "0",
                                        "--confirm-stove-cold-and-off",
                                        "--confirm-igniters-unplugged",
                                        "--confirm-actuator-loads-unplugged",
                                        "--confirm-correct-5v-ttl-wiring",
                                        "--confirm-j3-pin3-disconnected",
                                        "--confirm-adapter-vcc-disconnected",
                                        "--confirm-pickit-recovery-tested-on-spare",
                                        "--confirm-computer-power-stable",
                                        "--confirm-stove-power-stable",
                                        "--confirm-calibration-plan",
                                    ]
                                )
            self.assertEqual(result, 0)
            self.assertEqual(
                transport.break_states,
                [True, False, True, True, False, True],
            )
            self.assertEqual(opened.call_count, 3)
            self.assertEqual(transport.loader_entries, 2)
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["successful"])
            self.assertTrue(final["programming_performed"])
            self.assertFalse(final["recovery_required"])
            self.assertEqual(
                final["post_flash"]["identity"]["firmware_version"],
                "2.06",
            )
            self.assertFalse((session / "RECOVERY_REQUIRED.txt").exists())

    @unittest.skip("retired: manual AC/BREAK entry cannot reach E3 from the CLI")
    def test_post_flash_cold_boot_abort_releases_break_and_requires_recovery(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04", "fw206-format05"
        )

        def open_transport(_settings):
            transport.closed = False
            transport.break_active = False
            return transport

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "aborted-post-flash-cold-boot"
            with mock.patch(
                "openmaxfire.cli.SerialTransport", side_effect=open_transport
            ):
                with mock.patch(
                    "builtins.input",
                    side_effect=[
                        "POWER OFF FOR REHEARSAL",
                        "AC OFF USB OUT AFTER REHEARSAL",
                        "APPLICATION BOOTED AFTER REHEARSAL",
                        "USB CONNECTED AFTER REHEARSAL",
                        "POWER OFF FOR FLASH",
                        "ABORT",
                    ],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                with contextlib.redirect_stderr(io.StringIO()):
                                    result = main(
                                        [
                                            "--port", "SIM0",
                                            "--baud", "9600",
                                            "--request-delay", "0",
                                            "flash", str(FW206),
                                            "--session-dir", str(session),
                                            "--hold-tx-break-during-power-off",
                                            "--retry-delay", "0",
                                            "--confirm-stove-cold-and-off",
                                            "--confirm-igniters-unplugged",
                                            "--confirm-actuator-loads-unplugged",
                                            "--confirm-correct-5v-ttl-wiring",
                                            "--confirm-j3-pin3-disconnected",
                                            "--confirm-adapter-vcc-disconnected",
                                            "--confirm-pickit-recovery-tested-on-spare",
                                            "--confirm-computer-power-stable",
                                            "--confirm-stove-power-stable",
                                            "--confirm-calibration-plan",
                                        ]
                                    )
            self.assertEqual(result, 6)
            self.assertEqual(
                transport.break_states,
                [True, False, True, True, False, True, False],
            )
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["programming_performed"])
            self.assertTrue(final["recovery_required"])
            self.assertTrue((session / "RECOVERY_REQUIRED.txt").is_file())

    @unittest.skip("retired: public CLI no longer exposes physical rehearsal")
    def test_rehearsal_abort_releases_tx_break_without_loader_traffic(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04", "fw206-format05"
        )
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "aborted-break-rehearsal"
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch("builtins.input", return_value="ABORT"):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with contextlib.redirect_stdout(io.StringIO()):
                            with contextlib.redirect_stderr(io.StringIO()):
                                result = main(
                                    [
                                        "--port", "SIM0",
                                        "--baud", "9600",
                                        "--request-delay", "0",
                                        "flash", str(FW206),
                                        "--session-dir", str(session),
                                        "--rehearsal-only",
                                        "--hold-tx-break-during-power-off",
                                        "--retry-delay", "0",
                                        "--confirm-stove-cold-and-off",
                                        "--confirm-igniters-unplugged",
                                        "--confirm-actuator-loads-unplugged",
                                        "--confirm-correct-5v-ttl-wiring",
                                        "--confirm-j3-pin3-disconnected",
                                        "--confirm-adapter-vcc-disconnected",
                                        "--confirm-pickit-recovery-tested-on-spare",
                                        "--confirm-computer-power-stable",
                                        "--confirm-stove-power-stable",
                                        "--confirm-calibration-plan",
                                    ]
                                )
            self.assertEqual(result, 3)
            self.assertEqual(transport.break_states, [True, False])
            self.assertEqual(transport.loader_entries, 0)
            final = json.loads((session / "result.json").read_text())
            self.assertFalse(final["programming_performed"])

    @unittest.skip("superseded by the early public CLI E3 safety-lock tests")
    def test_live_cli_checks_physical_gates_before_opening_serial(self):
        from openmaxfire.cli import main

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "flash-session"
            with mock.patch("openmaxfire.cli.SerialTransport", side_effect=AssertionError):
                with contextlib.redirect_stderr(io.StringIO()):
                    result = main(
                        [
                            "--port", "SIM0",
                            "--baud", "9600",
                            "flash", str(FW206),
                            "--session-dir", str(session),
                        ]
                    )
            self.assertEqual(result, 4)
            self.assertFalse(session.exists())

    @unittest.skip("retired: public CLI no longer exposes physical rehearsal")
    def test_rehearsal_sends_nothing_after_handoff_until_passive_readiness(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04",
            "fw206-format05",
            emit_application_telemetry=False,
        )
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "flash-session"
            error = io.StringIO()
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch(
                    "builtins.input", return_value="POWER OFF FOR REHEARSAL"
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stderr(error):
                                result = main(
                                    [
                                        "--port", "SIM0",
                                        "--baud", "9600",
                                        "--request-delay", "0",
                                        "flash", str(FW206),
                                        "--rehearsal-only",
                                        "--session-dir", str(session),
                                        "--application-ready-timeout", "0.001",
                                        "--confirm-stove-cold-and-off",
                                        "--confirm-igniters-unplugged",
                                        "--confirm-correct-5v-ttl-wiring",
                                        "--confirm-j3-pin3-disconnected",
                                        "--confirm-adapter-vcc-disconnected",
                                        "--confirm-pickit-recovery-tested-on-spare",
                                        "--confirm-computer-power-stable",
                                        "--confirm-stove-power-stable",
                                        "--confirm-calibration-plan",
                                    ]
                                )
            self.assertEqual(result, 4)
            self.assertIn("no valid periodic telemetry", error.getvalue())
            self.assertEqual(transport.writes[-1], b"\xED")
            self.assertFalse(
                any(write.startswith(b"\xE3") for write in transport.writes)
            )
            self.assertFalse(
                any(
                    write == b"CR00"
                    for write in transport.writes[
                        transport.writes.index(b"\xED") + 1 :
                    ]
                )
            )

    @unittest.skip("retired: public CLI J3 recovery is locked before bundle access")
    def test_recovery_gate_failure_still_reports_unresolved_recovery(self):
        from openmaxfire.cli import main

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "failed-source"
            self._build_recovery_source(source)
            session = root / "recovery"
            with mock.patch("openmaxfire.cli.SerialTransport", side_effect=AssertionError):
                with contextlib.redirect_stderr(io.StringIO()):
                    result = main(
                        [
                            "--port", "SIM0",
                            "--baud", "9600",
                            "flash",
                            "--session-dir", str(session),
                            "--recover-from-session", str(source),
                        ]
                    )
            self.assertEqual(result, 6)
            self.assertFalse(session.exists())
            self.assertTrue((source / "RECOVERY_REQUIRED.txt").is_file())

    @unittest.skip("retired: public CLI J3 recovery cannot reach E3")
    def test_recovery_cli_needs_no_external_hex_and_replays_from_block_zero(self):
        from openmaxfire.cli import main

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "failed-source"
            preparation = self._build_recovery_source(source)
            session = root / "recovery"
            raw = bytes(
                preparation.eeprom_before[address] for address in range(0x100)
            )
            transport = SimulatedFlashSessionTransport(
                "fw202-format04",
                "fw206-format05",
                eeprom=raw,
                skip_rehearsal=True,
            )
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch("builtins.input", return_value="POWER OFF FOR FLASH"):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                result = main(
                                    [
                                        "--port", "SIM0",
                                        "--baud", "9600",
                                        "--request-delay", "0",
                                        "flash",
                                        "--session-dir", str(session),
                                        "--recover-from-session", str(source),
                                        "--retry-delay", "0",
                                        "--confirm-stove-cold-and-off",
                                        "--confirm-igniters-unplugged",
                                        "--confirm-actuator-loads-unplugged",
                                        "--confirm-correct-5v-ttl-wiring",
                                        "--confirm-j3-pin3-disconnected",
                                        "--confirm-adapter-vcc-disconnected",
                                        "--confirm-pickit-recovery-tested-on-spare",
                                        "--confirm-computer-power-stable",
                                        "--confirm-stove-power-stable",
                                        "--confirm-calibration-plan",
                                        "--confirm-recovery-target-matches-backup",
                                    ]
                                )
            self.assertEqual(result, 0)
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["successful"])
            self.assertTrue(final["programming_performed"])
            self.assertFalse(final["recovery_required"])
            self.assertEqual(transport.loader_entries, 2)
            self.assertTrue((session / "rescue" / FW206.name).is_file())
            self.assertFalse((source / "RECOVERY_REQUIRED.txt").exists())
            self.assertTrue((source / "RECOVERY_DELEGATED_TO.json").is_file())

    @unittest.skip("retired: public CLI cannot begin E3 programming")
    def test_cli_disconnect_after_programming_begins_leaves_recovery_marker(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04",
            "fw206-format05",
            programming_faults=SimulatedLoaderFaults(disconnect_after_blocks=3),
        )
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "interrupted"
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch(
                    "builtins.input",
                    side_effect=["POWER OFF FOR REHEARSAL", "POWER OFF FOR FLASH"],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                with contextlib.redirect_stderr(io.StringIO()):
                                    result = main(
                                        [
                                            "--port", "SIM0",
                                            "--baud", "9600",
                                            "--request-delay", "0",
                                            "flash", str(FW206),
                                            "--session-dir", str(session),
                                            "--retry-delay", "0",
                                            "--confirm-stove-cold-and-off",
                                            "--confirm-igniters-unplugged",
                                            "--confirm-actuator-loads-unplugged",
                                            "--confirm-correct-5v-ttl-wiring",
                                            "--confirm-j3-pin3-disconnected",
                                            "--confirm-adapter-vcc-disconnected",
                                            "--confirm-pickit-recovery-tested-on-spare",
                                            "--confirm-computer-power-stable",
                                            "--confirm-stove-power-stable",
                                            "--confirm-calibration-plan",
                                        ]
                                    )
            self.assertEqual(result, 6)
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["recovery_required"])
            self.assertEqual(final["loader"]["failure_outcome"], "transport_error")
            self.assertEqual(final["loader"]["blocks_completed"], 3)
            self.assertTrue((session / "RECOVERY_REQUIRED.txt").is_file())

    @unittest.skip("retired: public CLI cannot enter the programming phase")
    def test_cli_identify_failure_before_e3_is_not_mislabeled_as_new_damage(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04",
            "fw206-format05",
            programming_faults=SimulatedLoaderFaults(identify_failures=10),
        )
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "no-loader"
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch(
                    "builtins.input",
                    side_effect=["POWER OFF FOR REHEARSAL", "POWER OFF FOR FLASH"],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                with contextlib.redirect_stderr(io.StringIO()):
                                    result = main(
                                        [
                                            "--port", "SIM0",
                                            "--baud", "9600",
                                            "--request-delay", "0",
                                            "flash", str(FW206),
                                            "--session-dir", str(session),
                                            "--loader-identify-attempts", "2",
                                            "--retry-delay", "0",
                                            "--confirm-stove-cold-and-off",
                                            "--confirm-igniters-unplugged",
                                            "--confirm-actuator-loads-unplugged",
                                            "--confirm-correct-5v-ttl-wiring",
                                            "--confirm-j3-pin3-disconnected",
                                            "--confirm-adapter-vcc-disconnected",
                                            "--confirm-pickit-recovery-tested-on-spare",
                                            "--confirm-computer-power-stable",
                                            "--confirm-stove-power-stable",
                                            "--confirm-calibration-plan",
                                        ]
                                    )
            self.assertEqual(result, 5)
            final = json.loads((session / "result.json").read_text())
            self.assertFalse(final["programming_performed"])
            self.assertFalse(final["recovery_required"])
            self.assertFalse((session / "RECOVERY_REQUIRED.txt").exists())

    @unittest.skip("retired: public CLI cannot begin E3 programming")
    def test_cli_recovered_e5_finishes_but_blocks_operation_for_inspection(self):
        from openmaxfire.cli import main

        transport = SimulatedFlashSessionTransport(
            "fw202-format04",
            "fw206-format05",
            programming_faults=SimulatedLoaderFaults(write_failures={0: 1}),
        )
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "recovered-e5"
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch(
                    "builtins.input",
                    side_effect=["POWER OFF FOR REHEARSAL", "POWER OFF FOR FLASH"],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                with contextlib.redirect_stderr(io.StringIO()):
                                    result = main(
                                        [
                                            "--port", "SIM0",
                                            "--baud", "9600",
                                            "--request-delay", "0",
                                            "flash", str(FW206),
                                            "--session-dir", str(session),
                                            "--retry-delay", "0",
                                            "--confirm-stove-cold-and-off",
                                            "--confirm-igniters-unplugged",
                                            "--confirm-actuator-loads-unplugged",
                                            "--confirm-correct-5v-ttl-wiring",
                                            "--confirm-j3-pin3-disconnected",
                                            "--confirm-adapter-vcc-disconnected",
                                            "--confirm-pickit-recovery-tested-on-spare",
                                            "--confirm-computer-power-stable",
                                            "--confirm-stove-power-stable",
                                            "--confirm-calibration-plan",
                                        ]
                                    )
            self.assertEqual(result, 0)
            final = json.loads((session / "result.json").read_text())
            self.assertTrue(final["successful"])
            self.assertFalse(final["ready_for_operation"])
            self.assertTrue(final["hardware_inspection_required"])
            self.assertEqual(final["loader"]["write_failure_events"], 1)

    @unittest.skip("retired: public CLI cannot begin E3 programming")
    def test_postflash_verification_failure_is_persisted(self):
        from openmaxfire.cli import main

        raw = default_eeprom(PROFILES_BY_KEY["fw202-format04"])
        changed = bytearray(raw)
        changed[0x40] ^= 1
        transport = SimulatedFlashSessionTransport(
            "fw202-format04",
            "fw206-format05",
            eeprom=raw,
            post_eeprom=changed,
        )

        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "flash-session"
            with mock.patch("openmaxfire.cli.SerialTransport", return_value=transport):
                with mock.patch(
                    "builtins.input",
                    side_effect=["POWER OFF FOR REHEARSAL", "POWER OFF FOR FLASH"],
                ):
                    with mock.patch("openmaxfire.cli.time.sleep"):
                        with mock.patch(
                            "openmaxfire.cli.SleepInhibitor", FakeSleepInhibitor
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                with contextlib.redirect_stderr(io.StringIO()):
                                    result = main(
                                        [
                                            "--port", "SIM0",
                                            "--baud", "9600",
                                            "--request-delay", "0",
                                            "flash", str(FW206),
                                            "--session-dir", str(session),
                                            "--retry-delay", "0",
                                            "--confirm-stove-cold-and-off",
                                            "--confirm-igniters-unplugged",
                                            "--confirm-actuator-loads-unplugged",
                                            "--confirm-correct-5v-ttl-wiring",
                                            "--confirm-j3-pin3-disconnected",
                                            "--confirm-adapter-vcc-disconnected",
                                            "--confirm-pickit-recovery-tested-on-spare",
                                            "--confirm-computer-power-stable",
                                            "--confirm-stove-power-stable",
                                            "--confirm-calibration-plan",
                                        ]
                                    )
            self.assertEqual(result, 6)
            final = json.loads((session / "result.json").read_text())
            self.assertFalse(final["successful"])
            self.assertIn("EEPROM changed", final["message"])
            self.assertTrue(final["recovery_required"])
            self.assertTrue((session / "RECOVERY_REQUIRED.txt").is_file())


if __name__ == "__main__":
    unittest.main()
