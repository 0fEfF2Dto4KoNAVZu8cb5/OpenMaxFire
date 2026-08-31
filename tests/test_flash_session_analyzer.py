import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_PATH = Path(__file__).parents[1] / "tools" / "analyze_flash_sessions.py"
SPEC = importlib.util.spec_from_file_location("analyze_flash_sessions", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
analyzer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = analyzer
SPEC.loader.exec_module(analyzer)


def ihex_record(address, kind, payload=b""):
    body = bytes(
        (len(payload), (address >> 8) & 0xFF, address & 0xFF, kind)
    ) + payload
    return ":" + (body + bytes(((-sum(body)) & 0xFF,))).hex().upper()


def traffic(direction, data, monotonic_ns, sequence):
    return {
        "event": "traffic",
        "direction": direction,
        "data_hex": data.hex(" ").upper(),
        "byte_count": len(data),
        "monotonic_ns": monotonic_ns,
        "sequence": sequence,
        "created_utc": f"2026-08-30T00:00:{sequence:02d}+00:00",
    }


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class FlashSessionAnalyzerTests(unittest.TestCase):
    def build_fixture(self, root):
        sessions = root / "flash-sessions"
        session = sessions / "synthetic-001"
        session.mkdir(parents=True)

        image = "\n".join(
            (
                ihex_record(0, 0, b"\x34\x12\x78\x16"),
                ihex_record(0, 1),
                "",
            )
        ).encode("ascii")
        image_path = root / "reference.hex"
        image_path.write_bytes(image)
        image_sha = hashlib.sha256(image).hexdigest()

        correct = b"\xE3\x00\x00\x04\xD4\x12\x34\x16\x78"
        reversed_words = b"\xE3\x00\x00\x04\xD4\x34\x12\x78\x16"
        rows = [
            {"event": "session", "schema": "test"},
            traffic("tx", b"\xEA", 1_000_000_000, 1),
            traffic("rx", b"\xEB", 1_001_000_000, 2),
            traffic("tx", b"\xEA", 1_010_000_000, 3),
            traffic("tx", b"\xEA", 1_040_000_000, 4),
            traffic("tx", correct, 1_041_000_000, 5),
            traffic("rx", b"\xE7", 1_042_000_000, 6),
            traffic("tx", reversed_words, 1_043_000_000, 7),
            traffic("rx", b"\xE5", 1_044_000_000, 8),
            traffic("rx", b"\xE8", 1_045_000_000, 9),
            traffic("tx", b"\xED", 1_046_000_000, 10),
            traffic("rx", b"\xE4", 1_047_000_000, 11),
            # Loader-looking bytes inside an application chunk are not commands.
            traffic("rx", b"T00ea\n\xEA\xEB\xE4", 1_048_000_000, 12),
        ]
        write_jsonl(session / "loader-traffic.jsonl", rows)
        write_jsonl(
            session / "journal.jsonl",
            [
                {
                    "event": "session",
                    "metadata": {"image_sha256": image_sha},
                },
                {
                    "event": "loader_result",
                    "successful": False,
                    "loader_identified": True,
                    "program_blocks_sent": 2,
                },
            ],
        )
        (session / "loader-result.json").write_text(
            json.dumps(
                {
                    "schema": "openmaxfire.live-loader-result.v2",
                    "state": "failed",
                    "successful": False,
                    "loader_identified": True,
                    "image_sha256": image_sha,
                }
            ),
            encoding="utf-8",
        )

        raw = bytes(range(256))
        raw_sha = hashlib.sha256(raw).hexdigest()
        backup = {
            "schema": "openmaxfire.eeprom-backup.v1",
            "raw_hex": raw.hex().upper(),
            "eeprom": {f"A{address:02X}": f"{value:02X}" for address, value in enumerate(raw)},
        }
        (session / "eeprom-before.json").write_text(
            json.dumps(backup, sort_keys=True), encoding="utf-8"
        )
        (session / "preparation.json").write_text(
            json.dumps({"eeprom_before_sha256": raw_sha}), encoding="utf-8"
        )
        return sessions, raw_sha

    def test_counts_byte_order_eeprom_and_cadence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions, raw_sha = self.build_fixture(root)
            report = analyzer.analyze(root, sessions)

        self.assertEqual(
            report["totals"]["protocol_counts"],
            {"EA": 3, "EB": 1, "E3": 2, "E7": 1, "ED": 1, "E4": 1, "E5": 1, "E8": 1},
        )
        self.assertEqual(report["totals"]["e3_byte_order"]["high_byte_first"], 1)
        self.assertEqual(report["totals"]["e3_byte_order"]["low_byte_first"], 1)
        self.assertEqual(report["totals"]["eeprom_raw_sha256_counts"], {raw_sha: 1})
        cadence = report["logs"][0]["ea_cadence"]
        self.assertEqual(cadence["gap_count"], 2)
        self.assertEqual(cadence["min_gap_ms"], 10.0)
        self.assertEqual(cadence["median_gap_ms"], 20.0)
        self.assertEqual(cadence["mean_gap_ms"], 20.0)
        self.assertEqual(cadence["max_gap_ms"], 30.0)
        self.assertEqual(cadence["max_gap_evidence"]["before_sequence"], 3)
        self.assertEqual(cadence["max_gap_evidence"]["after_sequence"], 4)

    def test_report_and_cli_output_are_deterministic_and_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions, _ = self.build_fixture(root)
            evidence_path = sessions / "synthetic-001" / "loader-traffic.jsonl"
            before = evidence_path.read_bytes()
            first = analyzer.analyze(root, sessions)
            second = analyzer.analyze(root, sessions)
            self.assertEqual(first, second)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = analyzer.main(
                    ["--repo-root", str(root), "--sessions-root", str(sessions)]
                )
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue()), first)
            self.assertEqual(evidence_path.read_bytes(), before)

    def test_malformed_e3_is_reported_without_counting_payload_opcodes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            session = root / "flash-sessions" / "bad-frame"
            session.mkdir(parents=True)
            write_jsonl(
                session / "rehearsal-traffic.jsonl",
                [traffic("tx", b"\xE3\x00\x00\x02\x00\xEA", 1, 1)],
            )
            report = analyzer.analyze(root)

        self.assertEqual(report["totals"]["protocol_counts"]["E3"], 1)
        self.assertEqual(report["totals"]["protocol_counts"]["EA"], 0)
        self.assertEqual(report["totals"]["e3_byte_order"]["malformed"], 1)
        self.assertFalse(report["e3_frames"][0]["structurally_valid"])


if __name__ == "__main__":
    unittest.main()
