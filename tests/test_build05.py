
import unittest
from core import validate_qvac_envelope

class QvacEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.ok={'engine':'QVAC_LOCAL','model':'LLAMA_3_2_1B_INST_Q4_0','latency_ms':300,
                 'stop_reason':'eos','parsed':{'action':'LOG_FLUID','volume_ml':200,'unit':'ml','confidence':0.95}}
    def test_valid(self): self.assertEqual(validate_qvac_envelope(self.ok),200)
    def test_no_engine(self):
        self.ok.pop('engine')
        with self.assertRaisesRegex(ValueError,'QVAC_ENGINE_NOT_VERIFIED'):validate_qvac_envelope(self.ok)
    def test_cloud_engine_rejected(self):
        self.ok['engine']='CLOUD'
        with self.assertRaises(ValueError):validate_qvac_envelope(self.ok)
    def test_model_mismatch(self):
        self.ok['model']='OTHER'
        with self.assertRaisesRegex(ValueError,'QVAC_MODEL_NOT_VERIFIED'):validate_qvac_envelope(self.ok)
    def test_latency_bool(self):
        self.ok['latency_ms']=True
        with self.assertRaisesRegex(ValueError,'QVAC_LATENCY_INVALID'):validate_qvac_envelope(self.ok)
    def test_latency_negative(self):
        self.ok['latency_ms']=-1
        with self.assertRaises(ValueError):validate_qvac_envelope(self.ok)
    def test_incomplete(self):
        self.ok['stop_reason']='length'
        with self.assertRaisesRegex(ValueError,'QVAC_GENERATION_INCOMPLETE'):validate_qvac_envelope(self.ok)
    def test_missing_parsed(self):
        self.ok.pop('parsed')
        with self.assertRaises(ValueError):validate_qvac_envelope(self.ok)
    def test_low_confidence(self):
        self.ok['parsed']['confidence']=0.1
        with self.assertRaises(ValueError):validate_qvac_envelope(self.ok)
    def test_no_fake_fallback(self):
        self.ok['parsed']['action']='UNKNOWN'
        with self.assertRaises(ValueError):validate_qvac_envelope(self.ok)
