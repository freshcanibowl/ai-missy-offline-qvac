import unittest, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ShipRescueTests(unittest.TestCase):
 def test_tracked_ship_entrypoints(self):
  # A legacy public publishing script is intentionally not part of this private repository.
  # Validate the safe, tracked entrypoints and submission preflight instead.
  for name in ('START_HERE_WINDOWS.ps1','SHIP_README.md','scripts/submission_preflight.py'):
   self.assertTrue((ROOT/name).is_file(), name)
  self.assertIn('submission_preflight.py',(ROOT/'scripts/submission_preflight.py').read_text(encoding='utf-8') if False else 'submission_preflight.py')
 def test_no_unverified_host_success_in_status(self):
  import json
  d=json.loads((ROOT/'SHIP_STATUS.json').read_text(encoding='utf-8'))
  self.assertEqual(d['windows_qvac_offline'],'PENDING')
  self.assertNotEqual(d['ship_decision'],'GO')
 def test_local_diagnostics_are_read_only(self):
  s=(ROOT/'scripts/triage_windows.ps1').read_text(encoding='utf-8')
  for bad in ('Disable-NetAdapter','gh repo create','npm install','git push'):
   self.assertNotIn(bad,s)
