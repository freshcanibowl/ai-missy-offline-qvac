import json, tempfile, unittest, zipfile
from pathlib import Path
from scripts.ship_support import create_report, write_bundle

class ShipSupportTests(unittest.TestCase):
    def test_allowlist_excludes_identifiers(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'triage.json'
            p.write_text(json.dumps({'node':'v22.21.0','next_action':'RUN_PREPARE_ONLINE',
                'username':'private-user','patient_name':'Jane Doe','wifi_ssid':'PrivateWifi',
                'home_path':'C:/Users/Private'}),encoding='utf-8')
            report=create_report(p,False)
            serialized=json.dumps(report)
            for secret in ('private-user','Jane Doe','PrivateWifi','C:/Users/Private'):
                self.assertNotIn(secret,serialized)
            self.assertEqual(report['windows_diagnostics']['node'],'v22.21.0')
    def test_no_host_proof_claims(self):
        report=create_report(None,False)
        self.assertEqual(report['qvac_real_offline'],'NOT_VERIFIED_BY_THIS_SCRIPT')
        self.assertEqual(report['dorahacks_submitted'],'NOT_VERIFIED_BY_THIS_SCRIPT')
    def test_zip_contains_only_allowlisted_report(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'support.zip'
            write_bundle(out,None,False)
            with zipfile.ZipFile(out) as z:
                self.assertEqual(z.namelist(),['SHIP_SUPPORT_REDACTED.json'])
                self.assertEqual(json.loads(z.read(z.namelist()[0]))['scope'],'SYNTHETIC_DEMO_ONLY')
    def test_malformed_triage_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.json';p.write_text('[]')
            with self.assertRaises(ValueError): create_report(p,False)
