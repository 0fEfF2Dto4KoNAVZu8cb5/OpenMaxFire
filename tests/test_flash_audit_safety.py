import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from openmaxfire.audit import AuditTrail
from openmaxfire.client import MaxFireClient
from openmaxfire.errors import SafetyInterlockError
from openmaxfire.firmware import FirmwareImage
from openmaxfire.flashing import (
    FlashSafetyInterlocks,
    LiveLoaderPolicy,
    execute_live_loader_plan,
    live_flashing_supported,
    prepare_live_flash,
)
from openmaxfire.simulator import (
    SimulatedController,
    SimulatedLoaderTransport,
    SimulatedTransport,
)


ROOT = Path(__file__).resolve().parents[1]
FW206 = (
    ROOT
    / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex"
)


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
        "recovery_target_matches_backup": False,
    }
    values.update(overrides)
    return FlashSafetyInterlocks(**values)


class SpoofedPhysicalLoaderTransport(SimulatedLoaderTransport):
    """Subclass attempting to inherit the simulator-only exemption."""

    simulation_only = True
    qualified_loader_entry = True


class AttributeOnlyPhysicalTransport:
    """Non-simulator transport attempting both retired capability attributes."""

    simulation_only = True
    qualified_loader_entry = True

    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(bytes(data))

    def read(self, _size=1):
        return b""

    def close(self):
        return None


class FlashAuditSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        image = FirmwareImage.load(FW206)
        cls.safety = safe_interlocks()
        client = MaxFireClient(
            SimulatedTransport(SimulatedController("fw202-format04"))
        )
        try:
            cls.preparation = prepare_live_flash(
                client,
                image,
                port="SIM0",
                current_baudrate=9600,
                interlocks=cls.safety,
                request_delay=0,
            )
        finally:
            client.close()

    def _audit(self, directory, name="traffic.jsonl", **kwargs):
        return AuditTrail(
            Path(directory) / name,
            durable=True,
            buffered=True,
            **kwargs,
        )

    def test_public_physical_flashing_capability_is_disabled(self):
        self.assertFalse(live_flashing_supported())

    def test_spoofed_qualified_attribute_cannot_unlock_physical_e3(self):
        transports = (
            SpoofedPhysicalLoaderTransport(),
            AttributeOnlyPhysicalTransport(),
        )
        for index, transport in enumerate(transports):
            with self.subTest(transport=type(transport).__name__):
                with tempfile.TemporaryDirectory() as directory:
                    audit = self._audit(directory, name=f"traffic-{index}.jsonl")
                    try:
                        with self.assertRaises(SafetyInterlockError) as raised:
                            execute_live_loader_plan(
                                transport,
                                self.preparation,
                                interlocks=self.safety,
                                policy=LiveLoaderPolicy(retry_delay=0),
                                audit=audit,
                            )
                    finally:
                        audit.close()
                self.assertIn("subclasses cannot bypass", str(raised.exception))
                self.assertEqual(transport.writes, [])

    def test_probe_audit_record_failure_blocks_before_first_e3(self):
        transport = SimulatedLoaderTransport()
        with tempfile.TemporaryDirectory() as directory:
            audit = self._audit(directory)
            original_record = audit.record

            def fail_ea_record(direction, data):
                if direction == "tx" and bytes(data) == b"\xEA":
                    raise OSError("simulated EA record failure")
                return original_record(direction, data)

            try:
                with mock.patch.object(audit, "record", side_effect=fail_ea_record):
                    result = execute_live_loader_plan(
                        transport,
                        self.preparation,
                        interlocks=self.safety,
                        policy=LiveLoaderPolicy(retry_delay=0),
                        audit=audit,
                    )
            finally:
                audit.close()

        self.assertFalse(result.successful)
        self.assertFalse(result.recovery_required)
        self.assertEqual(transport.writes, [b"\xEA"])
        self.assertIn("no program block was sent", result.message)

    def test_first_e3_record_failure_blocks_without_creating_recovery_duty(self):
        transport = SimulatedLoaderTransport()
        with tempfile.TemporaryDirectory() as directory:
            audit = self._audit(directory)
            original_record = audit.record

            def fail_e3_record(direction, data):
                if direction == "tx" and bytes(data).startswith(b"\xE3"):
                    raise OSError("simulated first-E3 record failure")
                return original_record(direction, data)

            try:
                with mock.patch.object(audit, "record", side_effect=fail_e3_record):
                    result = execute_live_loader_plan(
                        transport,
                        self.preparation,
                        interlocks=self.safety,
                        policy=LiveLoaderPolicy(retry_delay=0),
                        audit=audit,
                    )
            finally:
                audit.close()

        self.assertFalse(result.successful)
        self.assertFalse(result.recovery_required)
        self.assertEqual([item for item in transport.writes if item[:1] == b"\xE3"], [])
        self.assertIn("no E3 frame was sent", result.message)

    def test_sink_without_durable_sync_blocks_first_e3(self):
        class MissingSyncAudit:
            buffered = True

            def record(self, _direction, _data):
                return None

        transport = SimulatedLoaderTransport()
        result = execute_live_loader_plan(
            transport,
            self.preparation,
            interlocks=self.safety,
            policy=LiveLoaderPolicy(retry_delay=0),
            audit=MissingSyncAudit(),
        )

        self.assertFalse(result.successful)
        self.assertFalse(result.recovery_required)
        self.assertEqual(transport.writes, [b"\xEA"])
        self.assertTrue(
            any("no sync_durable" in item for item in result.diagnostic_errors)
        )

    def test_first_e3_fsync_failure_blocks_but_preserves_existing_recovery_duty(self):
        transport = SimulatedLoaderTransport()
        recovery_preparation = replace(self.preparation, recovery_mode=True)
        recovery_safety = safe_interlocks(recovery_target_matches_backup=True)
        with tempfile.TemporaryDirectory() as directory:
            audit = self._audit(directory)
            original_sync = audit.sync_durable
            sync_count = 0

            def fail_first_e3_sync():
                nonlocal sync_count
                sync_count += 1
                if sync_count == 2:  # post-probe, first E3 intent
                    raise OSError("simulated first-E3 fsync failure")
                return original_sync()

            try:
                with mock.patch.object(
                    audit, "sync_durable", side_effect=fail_first_e3_sync
                ):
                    result = execute_live_loader_plan(
                        transport,
                        recovery_preparation,
                        interlocks=recovery_safety,
                        policy=LiveLoaderPolicy(retry_delay=0),
                        audit=audit,
                    )
            finally:
                audit.close()

        self.assertFalse(result.successful)
        self.assertTrue(result.recovery_required)
        self.assertEqual(
            [item for item in transport.writes if item[:1] == b"\xE3"], []
        )
        self.assertTrue(
            any("fsync failure" in item for item in result.diagnostic_errors)
        )

    def test_post_first_e3_record_failure_is_diagnostic_and_flash_finishes(self):
        transport = SimulatedLoaderTransport()
        with tempfile.TemporaryDirectory() as directory:
            audit = self._audit(directory)
            original_record = audit.record
            e3_intents = 0

            def fail_later_e3_records(direction, data):
                nonlocal e3_intents
                if direction == "tx" and bytes(data).startswith(b"\xE3"):
                    e3_intents += 1
                    if e3_intents > 1:
                        raise AttributeError("simulated later E3 record failure")
                return original_record(direction, data)

            try:
                with mock.patch("openmaxfire.audit.os.fsync"), mock.patch.object(
                    audit, "record", side_effect=fail_later_e3_records
                ):
                    result = execute_live_loader_plan(
                        transport,
                        self.preparation,
                        interlocks=self.safety,
                        policy=LiveLoaderPolicy(retry_delay=0),
                        audit=audit,
                    )
            finally:
                audit.close()

        self.assertTrue(result.successful)
        self.assertEqual(result.blocks_completed, result.blocks_total)
        self.assertTrue(
            any("record failure" in item for item in result.diagnostic_errors)
        )

    def test_post_first_e3_fsync_failure_is_diagnostic_and_flash_finishes(self):
        transport = SimulatedLoaderTransport()
        with tempfile.TemporaryDirectory() as directory:
            audit = self._audit(directory)
            original_sync = audit.sync_durable
            sync_count = 0

            def fail_later_e3_syncs():
                nonlocal sync_count
                sync_count += 1
                if sync_count >= 3:  # first E3 (call 2) was made durable
                    raise OSError("simulated later E3 fsync failure")
                return original_sync()

            try:
                with mock.patch("openmaxfire.audit.os.fsync"), mock.patch.object(
                    audit, "sync_durable", side_effect=fail_later_e3_syncs
                ):
                    result = execute_live_loader_plan(
                        transport,
                        self.preparation,
                        interlocks=self.safety,
                        policy=LiveLoaderPolicy(retry_delay=0),
                        audit=audit,
                    )
            finally:
                audit.close()

        self.assertTrue(result.successful)
        self.assertEqual(result.blocks_completed, result.blocks_total)
        self.assertTrue(
            any("fsync failure" in item for item in result.diagnostic_errors)
        )


if __name__ == "__main__":
    unittest.main()
