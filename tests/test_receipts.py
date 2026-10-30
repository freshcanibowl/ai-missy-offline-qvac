"""Synthetic validator unit tests. NOT QVAC runtime tests."""
import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_offline_receipts import verify
SMOKE={'engine':'QVAC_LOCAL','model':'LLAMA_3_2_1B_INST_Q4_0','model_loaded':True,'offline_inference_completed':True,'generated_text':'LOCAL','latency_ms':10}
PARSE={'engine':'QVAC_LOCAL','model':'LLAMA_3_2_1B_INST_Q4_0','parsed':{'action':'LOG_FLUID','volume_ml':200,'unit':'ml','confidence':0.95},'latency_ms':11}
class ReceiptTests(unittest.TestCase):
    def test_synthetic_valid_shape(self):self.assertEqual(verify(SMOKE,PARSE)['receipt_status'],'HOST_OBSERVED_QVAC_PASS')
    def test_reject_mock_engine(self):
        with self.assertRaises(ValueError):verify({**SMOKE,'engine':'MOCK'},PARSE)
    def test_reject_wrong_quantity(self):
        with self.assertRaises(ValueError):verify(SMOKE,{**PARSE,'parsed':{**PARSE['parsed'],'volume_ml':300}})
    def test_reject_unknown(self):
        with self.assertRaises(ValueError):verify(SMOKE,{**PARSE,'parsed':{**PARSE['parsed'],'action':'UNKNOWN'}})
    def test_reject_incomplete_smoke(self):
        with self.assertRaises(ValueError):verify({**SMOKE,'offline_inference_completed':False},PARSE)
    def test_reject_fake_confidence(self):
        with self.assertRaises(ValueError):verify(SMOKE,{**PARSE,'parsed':{**PARSE['parsed'],'confidence':0.4}})
    def test_reject_extra_schema(self):
        with self.assertRaises(ValueError):verify(SMOKE,{**PARSE,'parsed':{**PARSE['parsed'],'diagnosis':'safe'}})
if __name__=='__main__':unittest.main()
