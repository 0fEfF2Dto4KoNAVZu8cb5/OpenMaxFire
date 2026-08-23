import json
import tempfile
import unittest
from pathlib import Path

from openmaxfire.audit import AuditTrail
from openmaxfire.session import ControllerSession


class AuditTrailTests(unittest.TestCase):
    def test_session_records_identity_and_exposes_digestable_spans(self):
        audit = AuditTrail(metadata={"purpose": "test"}, session_id="fixed")
        with ControllerSession.simulated("fw202-format04", audit=audit) as session:
            checkpoint = audit.checkpoint()
            self.assertEqual(session.read_register(0x02), 0)
            span = audit.span(checkpoint)
            whole = audit.span()
        self.assertTrue(audit.closed)
        self.assertEqual(span.tx_bytes, 4)
        self.assertGreaterEqual(span.rx_bytes, 6)
        self.assertGreater(whole.event_count, span.event_count)
        self.assertEqual(len(span.sha256), 64)

    def test_jsonl_persistence_flushes_exact_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            audit = AuditTrail(path, metadata={"port": "SIM0"})
            audit.record("tx", b"CR00")
            audit.record("rx", b"CR0000\n")
            audit.close()
            rows = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(rows[0]["schema"], "openmaxfire.serial-audit.v1")
        self.assertEqual(rows[1]["data_hex"], "43 52 30 30")
        self.assertEqual(rows[2]["data_ascii"], "CR0000\\x0A")

    def test_span_digest_depends_on_boundaries_and_bytes_not_timestamps(self):
        first = AuditTrail(session_id="one")
        second = AuditTrail(session_id="two")
        for trail in (first, second):
            trail.record("tx", b"CR00")
            trail.record("rx", b"CR0000\n")
        self.assertEqual(first.span().sha256, second.span().sha256)
        self.assertNotEqual(first.span(1).sha256, first.span().sha256)


if __name__ == "__main__":
    unittest.main()
