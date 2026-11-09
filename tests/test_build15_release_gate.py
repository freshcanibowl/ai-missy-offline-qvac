import unittest
from scripts.build15_release_gate import assess,EXPECTED_HTTP
class TestReleaseGate(unittest.TestCase):
    def valid(self):
        return {'schema':'missy.build14.host-gate.v1','status':'LOCAL_SYNTHETIC_INTEGRATION_PASS','legacy_before':{'exit_code':0},'legacy_after':{'exit_code':0},'gates':{'legacy_python_regression':True,'synthetic_http':True},'http_tests':{k:True for k in EXPECTED_HTTP},'patch_apply':{'exit_code':0,'stdout_tail':'STATUS=PATCH_APPLIED'},'server_original_sha256':'a'*64,'server_patched_sha256':'b'*64}
    def test_good_synthetic_never_clinical(self):
        x=assess(self.valid());self.assertEqual(x['host_synthetic_evidence'],'PASS');self.assertEqual(x['clinical_and_production_release'],'NO_GO')
    def test_absent_receipt(self):self.assertEqual(assess({})['host_synthetic_evidence'],'FAIL')
    def test_http_claim_mismatch(self):
        x=self.valid();x['http_tests']['pair_not_sent']=False;self.assertEqual(assess(x)['host_synthetic_evidence'],'FAIL')
    def test_legacy_failed(self):
        x=self.valid();x['legacy_after']['exit_code']=1;self.assertEqual(assess(x)['host_synthetic_evidence'],'FAIL')
