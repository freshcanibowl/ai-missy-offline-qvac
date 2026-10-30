"""Build 22 offline care export tests; no QVAC model or network required."""
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from care_export import build_synthetic_export, SCHEMA_VERSION
from core import connect, confirm, add_reminder
from datetime import datetime, timezone, timedelta


class SyntheticCareExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "export.sqlite3"
        self.conn = connect(self.db)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_baseline_export_is_synthetic_and_versioned(self):
        export = build_synthetic_export(self.conn)
        self.assertEqual(export["schema_version"], SCHEMA_VERSION)
        self.assertIs(export["synthetic"], True)
        self.assertEqual(export["baseline_recorded_ml"], 700)
        self.assertEqual(export["recorded_total_ml"], 700)
        self.assertEqual(export["confirmed_events"], [])

    def test_confirmed_event_survives_restart_and_exports_offline(self):
        event_id = str(uuid.uuid4())
        confirm(self.conn, 200, "Log 200 ml water", event_id)
        self.conn.close()
        self.conn = connect(self.db)
        export = build_synthetic_export(self.conn)
        self.assertEqual(export["recorded_total_ml"], 900)
        self.assertEqual(export["confirmed_events"][0]["event_id"], event_id)
        self.assertEqual(export["confirmed_events"][0]["volume_ml"], 200)
        self.assertEqual(export["confirmed_events"][0]["origin"], "local-user-confirmed")

    def test_free_text_and_reminder_titles_are_not_exported(self):
        confirm(self.conn, 200, "Log 200 ml water SECRET_FREE_TEXT", str(uuid.uuid4()))
        due = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()
        add_reminder(self.conn, "SECRET_REMINDER_TITLE", due)
        output = json.dumps(build_synthetic_export(self.conn))
        self.assertNotIn("SECRET_FREE_TEXT", output)
        self.assertNotIn("SECRET_REMINDER_TITLE", output)
        self.assertNotIn('"source"', output)

    def test_reject_oversized_event_export(self):
        rows = [
            (str(uuid.uuid4()), 1, "Log 1 ml water", "2026-10-31T00:00:00+00:00")
            for _ in range(1001)
        ]
        with self.conn:
            self.conn.executemany(
                "INSERT INTO observations(id,ml,source,confirmed_at) VALUES(?,?,?,?)", rows
            )
        with self.assertRaisesRegex(ValueError, "EXPORT_TOO_LARGE"):
            build_synthetic_export(self.conn)


if __name__ == "__main__":
    unittest.main()
