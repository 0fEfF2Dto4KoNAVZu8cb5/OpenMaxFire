import contextlib
import hashlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "build_pickit_recovery_image.py"
SPEC = importlib.util.spec_from_file_location("build_pickit_recovery_image", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)

DONOR = ROOT / "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex"
REFERENCE = ROOT / "reverse-engineering/firmware/2.02/extracted/Bixby_0202_260827_PICkit.hex"
class PickitHybridBuilderTests(unittest.TestCase):
    def test_candidate_manifest_explicitly_forbids_programming(self):
        reference = builder.FirmwareImage.load(REFERENCE)
        controller_memory = dict(reference.intel_hex.memory)
        for word_address, (_before, after) in builder.EXPECTED_INCIDENT_PROGRAM_DIFFS.items():
            byte_address = 2 * word_address
            controller_memory[byte_address] = after & 0xFF
            controller_memory[byte_address + 1] = (after >> 8) & 0xFF
        controller_bytes = builder.serialize_intel_hex(controller_memory)

        with tempfile.TemporaryDirectory() as directory:
            controller = Path(directory) / "synthetic-incident-read.hex"
            controller.write_bytes(controller_bytes)
            _output, manifest = builder.build_unqualified_candidate(
                donor_path=DONOR,
                reference_path=REFERENCE,
                controller_path=controller,
                expected_controller_sha256=hashlib.sha256(controller_bytes).hexdigest(),
            )

        self.assertEqual(manifest["status"], "unqualified_experimental_candidate")
        self.assertFalse(manifest["safe_to_import_in_ipe"])
        self.assertFalse(manifest["programming_authorized"])
        self.assertTrue(any("DO NOT program" in item for item in manifest["warnings"]))

    def test_cli_refuses_to_emit_candidate_without_analysis_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate.hex"
            manifest = Path(directory) / "candidate.json"
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                result = builder.main(
                    [
                        "--donor", str(DONOR),
                        "--reference", str(REFERENCE),
                        "--controller-dump", "not-opened.hex",
                        "--expected-controller-sha256", "0" * 64,
                        "--output", str(output),
                        "--manifest", str(manifest),
                    ]
                )

            self.assertEqual(result, 2)
            self.assertFalse(output.exists())
            self.assertFalse(manifest.exists())
            self.assertIn("unqualified format-04/2.06 hybrid", error.getvalue())


if __name__ == "__main__":
    unittest.main()
