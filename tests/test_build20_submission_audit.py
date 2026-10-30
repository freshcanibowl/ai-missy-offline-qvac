import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build20', ROOT / 'scripts/build20_submission_audit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Build20Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.names = ['qvac-verified-20261030-230025.json', 'qvac-http-e2e-20261030-230025.json']
        # Local fixtures cannot reproduce the actual user receipt hashes; use the
        # exact SHA-256 of the fixture bytes only within this test.
        self.paths = [self.root / x for x in self.names]
        self.paths[0].write_text('synthetic fixture QVAC', encoding='utf-8')
        self.paths[1].write_text('synthetic fixture E2E', encoding='utf-8')
        self.original = dict(m.EXPECTED)
        m.EXPECTED.clear()
        m.EXPECTED.update({'qvac_receipt': m.digest(self.paths[0]), 'http_e2e_receipt': m.digest(self.paths[1])})
        self.addCleanup(lambda: (m.EXPECTED.clear(), m.EXPECTED.update(self.original)))
        self.manifest = {
            'schema': 'ai-missy-build19-redacted-evidence/1',
            'source_receipt_filenames': self.names,
            'technical_receipt_integrity': 'PASS',
            'sha256': dict(m.EXPECTED),
            'checks': {k: True for k in m.EXPECTED_CHECKS}
        }

    def test_pass_still_no_go(self):
        r = m.verify(self.manifest, self.root)
        self.assertEqual(r['technical_evidence'], 'PASS_HASHES_AND_SEMANTIC_RECEIPTS')
        self.assertEqual(r['readiness'], 'NO_GO')
        self.assertEqual(r['video']['independent_review'], 'PENDING')

    def test_mutated_receipt_fails(self):
        self.paths[0].write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'ON_DISK_HASH_MISMATCH'):
            m.verify(self.manifest, self.root)

    def test_missing_check_fails(self):
        self.manifest['checks']['safety_checks'] = False
        with self.assertRaisesRegex(ValueError, 'BUILD19_CHECKS'):
            m.verify(self.manifest, self.root)

    def test_path_traversal_rejected(self):
        self.manifest['source_receipt_filenames'][0] = '../private.json'
        with self.assertRaisesRegex(ValueError, 'SOURCE_RECEIPT_NAME_UNSAFE'):
            m.verify(self.manifest, self.root)

    def test_zip_contains_only_redacted_report_and_readme(self):
        report = m.verify(self.manifest, self.root)
        output = self.root / 'report.json'
        bundle = self.root / 'bundle.zip'
        m.write_package(report, output, bundle)
        import zipfile
        with zipfile.ZipFile(bundle) as z:
            self.assertEqual(set(z.namelist()), {'BUILD20_SUBMISSION_READINESS.json', 'JUDGE_REVIEW_README.md'})
            self.assertNotIn(str(self.root), z.read('BUILD20_SUBMISSION_READINESS.json').decode())

if __name__ == '__main__':
    unittest.main()
