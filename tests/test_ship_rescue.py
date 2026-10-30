import unittest
import pathlib
import json

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ShipRescueTests(unittest.TestCase):
    def test_tracked_ship_entrypoints(self):
        # Legacy public publisher is intentionally excluded from private Git.
        required = ('START_HERE_WINDOWS.ps1', 'SHIP_README.md',
                    'scripts/submission_preflight.py')
        for name in required:
            self.assertTrue((ROOT / name).is_file(), name)
        preflight = (ROOT / 'scripts/submission_preflight.py').read_text(encoding='utf-8')
        self.assertIn('START_HERE_WINDOWS.ps1', preflight)
        self.assertIn('SHIP_README.md', preflight)

    def test_no_unverified_host_success_in_status(self):
        d = json.loads((ROOT / 'SHIP_STATUS.json').read_text(encoding='utf-8'))
        self.assertEqual(d['windows_qvac_offline'], 'PENDING')
        self.assertNotEqual(d['ship_decision'], 'GO')

    def test_local_diagnostics_are_read_only(self):
        s = (ROOT / 'scripts/triage_windows.ps1').read_text(encoding='utf-8')
        for bad in ('Disable-NetAdapter', 'gh repo create', 'npm install', 'git push'):
            self.assertNotIn(bad, s)
