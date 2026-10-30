import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'build19_evidence_package.py'
spec = importlib.util.spec_from_file_location('build19_evidence_package', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Build19EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.q = self.root / 'qvac-verified-20261030-230025.json'
        self.e = self.root / 'qvac-http-e2e-20261030-230025.json'
        self.q.write_text(json.dumps({'receipt_status': 'HOST_OBSERVED_QVAC_PASS', 'model': m.MODEL}))
        self.e.write_text(json.dumps({'result': 'HOST_OBSERVED_E2E_PASS', 'engine': m.ENGINE, 'model': m.MODEL,
                                      'synthetic': True, 'initial_recorded_ml': 700, 'confirmed_recorded_ml': 900,
                                      'confirmation_persisted': True, 'replay_rejected': True, 'food_abstention': True}))

    def test_matching_receipts_pass_but_release_no_go(self):
        r = m.build(self.root, m.sha256(self.q), m.sha256(self.e))
        self.assertEqual(r['technical_receipt_integrity'], 'PASS')
        self.assertEqual(r['public_release'], 'NO_GO')
        self.assertEqual(r['video']['independent_review'], 'PENDING')

    def test_hash_mismatch_fails_closed(self):
        r = m.build(self.root, '0' * 64, m.sha256(self.e))
        self.assertEqual(r['technical_receipt_integrity'], 'FAIL')

    def test_semantic_failure_fails_closed(self):
        e = json.loads(self.e.read_text())
        e['food_abstention'] = False
        self.e.write_text(json.dumps(e))
        r = m.build(self.root, m.sha256(self.q), m.sha256(self.e))
        self.assertEqual(r['technical_receipt_integrity'], 'FAIL')

    def test_no_paths_or_raw_data_in_report(self):
        r = m.build(self.root, m.sha256(self.q), m.sha256(self.e))
        self.assertNotIn(str(self.root), json.dumps(r))
        self.assertNotIn('generated_text', json.dumps(r))

if __name__ == '__main__':
    unittest.main()
