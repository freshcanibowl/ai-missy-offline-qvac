import unittest, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ShipRescueTests(unittest.TestCase):
 def test_git_publish_includes_entrypoint(self):
  s=(ROOT/'scripts/publish-new-repo.ps1').read_text()
  self.assertIn('START_HERE_WINDOWS.ps1',s)
  self.assertIn('SHIP_README.md',s)
  self.assertIn('submission_preflight.py',s)
 def test_no_unverified_host_success_in_status(self):
  import json
  d=json.loads((ROOT/'SHIP_STATUS.json').read_text())
  self.assertEqual(d['windows_qvac_offline'],'PENDING')
  self.assertNotEqual(d['ship_decision'],'GO')
 def test_local_diagnostics_are_read_only(self):
  s=(ROOT/'scripts/triage_windows.ps1').read_text()
  for bad in ('Disable-NetAdapter','gh repo create','npm install','git push'):
   self.assertNotIn(bad,s)
