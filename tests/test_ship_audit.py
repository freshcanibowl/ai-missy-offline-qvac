
import unittest,tempfile,json,pathlib
from scripts.ship_audit import audit
class ShipAuditTests(unittest.TestCase):
    def test_no_evidence_never_go(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(d,'','','')
            self.assertEqual(r['decision'],'NO_GO_UNTIL_EXTERNAL_VERIFICATION')
            self.assertEqual(r['results']['qvac_host_observed']['status'],'PENDING')
    def test_fake_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'qvac-verified-20261029.json'
            p.write_text(json.dumps({'receipt_status':'HOST_OBSERVED_QVAC_PASS','model':'LLAMA_3_2_1B_INST_Q4_0'}))
            self.assertEqual(audit(d,'','','')['results']['qvac_host_observed']['status'],'PENDING')
    def test_repo_url_is_not_verified(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(d,'','https://github.com/example/repo','')
            self.assertEqual(r['results']['public_repo']['status'],'URL_PROVIDED_UNVERIFIED')
