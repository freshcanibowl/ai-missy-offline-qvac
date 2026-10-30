"""Build 23 synthetic care timeline regression tests; no network required."""
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from care_timeline import build_synthetic_timeline, SCHEMA_VERSION
from core import connect, confirm


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "timeline.sqlite3"
        self.conn = connect(self.db)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def _add(self, volume, note=None):
        event_id = str(uuid.uuid4())
        confirm(self.conn, volume, note or f"Log {volume} ml water", event_id)
        return event_id

    def test_empty_timeline_is_explicitly_synthetic(self):
        result = build_synthetic_timeline(self.conn)
        self.assertEqual(result["schema_version"], SCHEMA_VERSION)
        self.assertIs(result["synthetic"], True)
        self.assertEqual(result["page"]["total"], 0)
        self.assertEqual(result["events"], [])

    def test_confirmed_record_survives_reopen(self):
        event_id = self._add(200)
        self.conn.close()
        self.conn = connect(self.db)
        result = build_synthetic_timeline(self.conn)
        self.assertEqual(result["page"]["total"], 1)
        self.assertEqual(result["events"][0]["event_id"], event_id)
        self.assertEqual(result["events"][0]["volume_ml"], 200)
        self.assertEqual(result["events"][0]["event_type"], "FLUID_INTAKE_RECORDED")
        self.assertFalse(result["events"][0]["cryptographic_attestation"])

    def test_pagination_is_bounded_and_complete(self):
        self._add(100)
        self._add(200)
        self._add(300)
        first = build_synthetic_timeline(self.conn, limit=2, offset=0)
        second = build_synthetic_timeline(self.conn, limit=2, offset=2)
        self.assertEqual(first["page"]["total"], 3)
        self.assertTrue(first["page"]["has_more"])
        self.assertFalse(second["page"]["has_more"])
        ids = [e["event_id"] for e in first["events"] + second["events"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 3)

    def test_rejects_invalid_pagination_and_bool(self):
        for limit, offset in [(0, 0), (51, 0), (True, 0), (1, -1),
                              (1, 1001), (1, True), ("20", 0)]:
            with self.subTest(limit=limit, offset=offset), self.assertRaises(ValueError):
                build_synthetic_timeline(self.conn, limit=limit, offset=offset)

    def test_no_raw_text_or_reminders_leak(self):
        self._add(200, "Log 200 ml water PRIVATE_FREE_TEXT")
        result = json.dumps(build_synthetic_timeline(self.conn))
        self.assertNotIn("PRIVATE_FREE_TEXT", result)
        self.assertNotIn('"source"', result)
        self.assertNotIn('"reminders"', result)

    def test_rejects_malformed_persisted_timestamp(self):
        self.conn.execute(
            "INSERT INTO observations(id,ml,source,confirmed_at) VALUES(?,?,?,?)",
            (str(uuid.uuid4()), 100, "Log 100 ml water", "not-a-date"),
        )
        self.conn.commit()
        with self.assertRaisesRegex(ValueError, "TIMELINE_EVENT_INVALID"):
            build_synthetic_timeline(self.conn)


if __name__ == "__main__":
    unittest.main()
