from pathlib import Path
import unittest

from openmaxfire.experimental_flasher import (
    ExperimentalFlasherError,
    ExperimentalJ3Flasher,
    PhysicalFlasherPolicy,
    dry_run_image,
    protected_test_block,
    validate_j3_image,
)
from openmaxfire.firmware import FirmwareImage, FirmwareImageError, LOADER_PROTECTED_START
from openmaxfire.simulator import SimulatedLoaderFaults, SimulatedLoaderTransport


ROOT = Path(__file__).resolve().parents[1]
FW206_PICKIT = ROOT / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex"
FW270 = ROOT / "reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex"


class TimeoutAwareLoaderTransport(SimulatedLoaderTransport):
    def __init__(self):
        super().__init__()
        self.timeout = 0.25
        self.timeout_history: list[float] = []

    def set_timeout(self, timeout: float) -> None:
        self.timeout = float(timeout)
        self.timeout_history.append(self.timeout)


class ExperimentalFlasherTests(unittest.TestCase):
    def test_protected_test_block_targets_skip_range(self):
        block = protected_test_block()
        self.assertEqual(block.word_address, LOADER_PROTECTED_START)
        self.assertEqual(block.frame[0], 0xE3)

    def test_protected_test_changes_no_flash(self):
        initial = {LOADER_PROTECTED_START: 0x1234, LOADER_PROTECTED_START + 1: 0x2345}
        transport = SimulatedLoaderTransport(initial_program_words=initial)
        flasher = ExperimentalJ3Flasher(
            transport,
            policy=PhysicalFlasherPolicy(identify_attempts=1, timeout_retries=0, checksum_retries=0),
        )
        result = flasher.run_protected_test()
        self.assertTrue(result["success"])
        self.assertEqual(transport.flash_words, initial)
        self.assertTrue(transport.application_running)

    def test_identify_temporarily_uses_fast_timeout_then_restores_operation_timeout(self):
        transport = TimeoutAwareLoaderTransport()
        flasher = ExperimentalJ3Flasher(
            transport,
            policy=PhysicalFlasherPolicy(
                identify_attempts=1,
                identify_interval=0.015,
                identify_read_timeout=0.010,
            ),
        )
        attempt = flasher.identify()
        self.assertEqual(attempt, 1)
        self.assertEqual(transport.timeout_history, [0.010, 0.25])
        self.assertEqual(transport.timeout, 0.25)

    def test_full_270_image_succeeds_in_loader_simulator(self):
        image = FirmwareImage.load(FW270)
        transport = SimulatedLoaderTransport()
        flasher = ExperimentalJ3Flasher(
            transport,
            policy=PhysicalFlasherPolicy(identify_attempts=1, timeout_retries=0, checksum_retries=0),
        )
        result = flasher.flash(image)
        self.assertTrue(result["success"])
        self.assertEqual(result["blocks_completed"], result["blocks_total"])
        self.assertTrue(transport.application_running)

    def test_e5_aborts_immediately_without_bixcheck_style_retries(self):
        image = FirmwareImage.load(FW270)
        first_address = min(image.program_words)
        faults = SimulatedLoaderFaults(write_failures={first_address: 1})
        transport = SimulatedLoaderTransport(faults=faults)
        flasher = ExperimentalJ3Flasher(
            transport,
            policy=PhysicalFlasherPolicy(
                identify_attempts=1,
                timeout_retries=5,
                checksum_retries=5,
                unexpected_retries=5,
            ),
        )
        with self.assertRaisesRegex(ExperimentalFlasherError, "E5"):
            flasher.flash(image)
        block_frames = [item for item in transport.writes if item.startswith(b"\xE3")]
        self.assertEqual(len(block_frames), 1)

    def test_e8_can_retry_with_small_explicit_limit(self):
        image = FirmwareImage.load(FW270)
        first_address = min(image.program_words)
        faults = SimulatedLoaderFaults(checksum_failures={first_address: 1})
        transport = SimulatedLoaderTransport(faults=faults)
        flasher = ExperimentalJ3Flasher(
            transport,
            policy=PhysicalFlasherPolicy(identify_attempts=1, checksum_retries=1),
        )
        result = flasher.flash(image)
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["retries"], 1)

    def test_pickit_image_is_rejected(self):
        image = FirmwareImage.load(FW206_PICKIT)
        with self.assertRaisesRegex(FirmwareImageError, "PICkit"):
            validate_j3_image(image)
        with self.assertRaises(FirmwareImageError):
            dry_run_image(image)

    def test_dry_run_accepts_270_without_transport(self):
        image = FirmwareImage.load(FW270)
        result = dry_run_image(image)
        self.assertEqual(result["firmware_version"], "2.70")
        self.assertGreater(result["block_count"], 1)


if __name__ == "__main__":
    unittest.main()
