import unittest
from dataclasses import replace
from metabolic.privacy_gate import AccessDenied,AccessDecision,authorize_read,read_policy_for_endpoint
GOOD=AccessDecision('synthetic','synthetic','view_own_records','metabolic_entries',True,True,True,True)
class TestPrivacyGate(unittest.TestCase):
    def denied(self,d,resource='metabolic_entries'):
        with self.assertRaises(AccessDenied):authorize_read(d,expected_resource=resource)
    def test_missing_identity(self):self.denied(None)
    def test_untyped_claim(self):self.denied({'authorized':True})
    def test_cross_subject(self):self.denied(replace(GOOD,subject_id='another'))
    def test_wrong_resource(self):self.denied(replace(GOOD,resource='pair_preview'))
    def test_missing_identity_check(self):self.denied(replace(GOOD,verified_identity=False))
    def test_missing_consent(self):self.denied(replace(GOOD,verified_consent=False))
    def test_missing_binding(self):self.denied(replace(GOOD,verified_subject_binding=False))
    def test_untrusted_point(self):self.denied(replace(GOOD,from_trusted_enforcement_point=False))
    def test_wrong_purpose(self):self.denied(replace(GOOD,purpose='change_medication'))
    def test_all_true_claim_fails(self):self.denied(GOOD)
    def test_pair_export_fails(self):self.denied(replace(GOOD,resource='pair_preview',purpose='patient_review_export'),'pair_preview')
    def test_unknown_resource(self):self.denied(GOOD,'unknown')
    def test_routes(self):
        self.assertEqual(read_policy_for_endpoint('/api/metabolic/entries'),'metabolic_entries')
        self.assertEqual(read_policy_for_endpoint('/api/metabolic/pair-preview'),'pair_preview')
        self.assertIsNone(read_policy_for_endpoint('/api/metabolic/i18n'))
