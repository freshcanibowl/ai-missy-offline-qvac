"""Build31 synthetic handoff integrity, authorization and stale evidence tests."""
import unittest
from dataclasses import replace, FrozenInstanceError

from metabolic.consent_contract import SyntheticAceContract
from metabolic.longitudinal_memory import Observation, SyntheticMemoryLedger, AccessDenied, IntegrityError
from metabolic.evidence_handoff import SyntheticHandoffService, HandoffRejected

T="2026-11-27T11:00:00+08:00"
PAT="SYN-PATIENT-001"
READER="SYN-NURSE-001"
P="care_demo_review"


def example(event_id="SYN-GL-001", **kwargs):
    values=dict(event_id=event_id,module="glucose",event="check_in",
                observed_at="2026-11-20T09:00:00+08:00",
                recorded_at="2026-11-20T09:04:00+08:00",
                source="synthetic_patient_demo", evidence_id="SYN-EV-001")
    values.update(kwargs)
    return Observation(**values)


class EvidenceBoundHandoffBuild31(unittest.TestCase):
    def setUp(self):
        self.ace=SyntheticAceContract(testing_key=b"synthetic-test-key-only-0123456789abcdef")
        self.ledger=SyntheticMemoryLedger(authorization=self.ace)
        self.svc=SyntheticHandoffService(ledger=self.ledger)
        self.event=example()
        self.ledger.create(self.event)
        self.token=self.ace.issue_fixture(
            grant_id="SYN-GRANT-001",subject=PAT,grantee=READER,purpose=P,
            issued_at="2026-11-01T00:00:00+08:00",
            valid_until="2026-12-01T00:00:00+08:00")
    def params(self,**kwargs):
        fields=dict(token=self.token,subject=PAT,grantee=READER,purpose=P,at=T)
        fields.update(kwargs)
        return fields
    def receipt(self,**kwargs):
        return self.svc.issue_receipt(event_id=self.event.event_id,**self.params(**kwargs))
    def inspect(self,receipt,**kwargs):
        return self.svc.inspect(receipt_id=receipt.receipt_id,**self.params(**kwargs))

    def test_01_authorized_synthetic_handoff_preview(self):
        r=self.receipt()
        v=self.inspect(r)
        self.assertEqual(v.version,1)
        self.assertEqual(v.evidence_id,"SYN-EV-001")
        self.assertEqual(v.revision_hash,self.ledger._revisions[-1].content_hash)
        self.assertTrue(v.synthetic)
        self.assertEqual(v.scope,"demo_only")
        self.assertEqual(v.confirmation,"unverified")
    def test_02_readonly_preview_and_receipt(self):
        r=self.receipt()
        with self.assertRaises(FrozenInstanceError):
            r.version=4
        with self.assertRaises(FrozenInstanceError):
            self.inspect(r).source="clinical_ehr"
    def test_03_missing_grant_denied_before_issue(self):
        with self.assertRaises(AccessDenied):
            self.receipt(token=None)
    def test_04_missing_grant_denied_at_inspection(self):
        r=self.receipt()
        with self.assertRaises(AccessDenied):
            self.inspect(r,token=None)
    def test_05_grant_revocation_blocks_existing_receipt(self):
        r=self.receipt()
        self.assertTrue(self.ace.revoke(self.token.grant_id))
        with self.assertRaises(AccessDenied):
            self.inspect(r)
    def test_06_expired_grant_denied(self):
        r=self.receipt()
        with self.assertRaises(AccessDenied):
            self.inspect(r,at="2026-12-01T01:00:00+08:00")
    def test_07_wrong_subject_denied(self):
        r=self.receipt()
        with self.assertRaises(AccessDenied):
            self.inspect(r,subject="SYN-PATIENT-002")
    def test_08_wrong_grantee_denied(self):
        r=self.receipt()
        with self.assertRaises(AccessDenied):
            self.inspect(r,grantee="SYN-NURSE-002")
    def test_09_wrong_purpose_denied(self):
        r=self.receipt()
        with self.assertRaises(HandoffRejected):
            self.inspect(r,purpose="audit_demo")
    def test_10_tampered_signature_denied(self):
        r=self.receipt()
        with self.assertRaises(AccessDenied):
            self.inspect(r,token=replace(self.token,signature="0"*64))
    def test_11_corrected_event_invalidates_previous_receipt(self):
        r=self.receipt()
        self.ledger.correct(replace(self.event,evidence_id="SYN-EV-002"),expected_version=1)
        with self.assertRaisesRegex(HandoffRejected,"STALE"):
            self.inspect(r)
    def test_12_retracted_event_invalidates_previous_receipt(self):
        r=self.receipt()
        self.ledger.retract(self.event.event_id,expected_version=1)
        with self.assertRaisesRegex(HandoffRejected,"STALE"):
            self.inspect(r)
    def test_13_new_receipt_reflects_corrected_event(self):
        self.ledger.correct(replace(self.event,evidence_id="SYN-EV-002"),expected_version=1)
        r=self.receipt()
        self.assertEqual(self.inspect(r).version,2)
        self.assertEqual(self.inspect(r).evidence_id,"SYN-EV-002")
    def test_14_retracted_event_cannot_issue(self):
        self.ledger.retract(self.event.event_id,expected_version=1)
        with self.assertRaisesRegex(HandoffRejected,"NOT_ACTIVE"):
            self.receipt()
    def test_15_unrelated_ledger_mutation_invalidates_snapshot(self):
        r=self.receipt()
        self.ledger.create(example("SYN-BP-001",module="pressure",event="review"))
        with self.assertRaisesRegex(HandoffRejected,"STALE"):
            self.inspect(r)
    def test_16_hash_chain_tamper_rejected(self):
        r=self.receipt()
        self.ledger._revisions[0]=replace(self.ledger._revisions[0],content_hash="bad")
        with self.assertRaises(IntegrityError):
            self.inspect(r)
    def test_17_observation_tamper_rejected(self):
        r=self.receipt()
        self.ledger._revisions[0]=replace(self.ledger._revisions[0],
                                         observation=replace(self.event,source="synthetic_care_plan"))
        with self.assertRaises(IntegrityError):
            self.inspect(r)
    def test_18_manifest_tamper_rejected(self):
        r=self.receipt()
        self.svc._receipts[r.receipt_id]=replace(r,revision=99)
        with self.assertRaisesRegex(IntegrityError,"MANIFEST"):
            self.inspect(r)
    def test_19_fake_receipt_is_not_trusted(self):
        r=self.receipt()
        with self.assertRaisesRegex(HandoffRejected,"UNKNOWN_RECEIPT"):
            self.svc.inspect(receipt_id="SYN-HANDOFF-"+"0"*24,**self.params())
        self.assertIsNotNone(r)
    def test_20_invalid_event_name_denied(self):
        with self.assertRaises(HandoffRejected):
            self.svc.issue_receipt(event_id="../SYN-GL-001",**self.params())
    def test_21_missing_event_denied_after_authorization(self):
        with self.assertRaisesRegex(HandoffRejected,"NOT_ACTIVE"):
            self.svc.issue_receipt(event_id="SYN-MISSING-001",**self.params())
    def test_22_no_automatic_reissue_after_consent_revocation(self):
        self.ace.revoke(self.token.grant_id)
        with self.assertRaises(AccessDenied):
            self.receipt()
    def test_23_new_independent_grant_can_read_only_current_evidence(self):
        old=self.receipt()
        self.ace.revoke(self.token.grant_id)
        fresh=self.ace.issue_fixture(
            grant_id="SYN-GRANT-002",subject=PAT,grantee=READER,purpose=P,
            issued_at="2026-11-20T00:00:00+08:00",valid_until="2026-12-02T00:00:00+08:00")
        with self.assertRaises(AccessDenied):
            self.inspect(old)
        new=self.receipt(token=fresh)
        self.assertEqual(self.inspect(new,token=fresh).version,1)
    def test_24_receipt_does_not_contain_raw_observation_source_or_value(self):
        r=self.receipt()
        self.assertFalse(hasattr(r,"observation"))
        self.assertFalse(hasattr(r,"source"))
        self.assertFalse(hasattr(r,"evidence_id"))
    def test_25_chain_tip_and_event_revision_bound(self):
        r=self.receipt()
        self.assertEqual(r.chain_tip,self.ledger._revisions[-1].content_hash)
        self.assertEqual(r.revision_hash,self.ledger._revisions[-1].content_hash)
        self.assertEqual(len(r.manifest_hash),64)
    def test_26_readonly_preview_is_not_clinical_finding(self):
        r=self.receipt()
        self.assertEqual(self.inspect(r).note,"SYNTHETIC_ONLY_NOT_CLINICAL_EVIDENCE")
    def test_27_no_authority_defaults_to_denial(self):
        isolated=SyntheticMemoryLedger()
        isolated.create(self.event)
        service=SyntheticHandoffService(ledger=isolated)
        with self.assertRaises(AccessDenied):
            service.issue_receipt(event_id=self.event.event_id,**self.params())
    def test_28_wrong_credential_on_valid_receipt_denied(self):
        r=self.receipt()
        with self.assertRaises(AccessDenied):
            self.inspect(r,token="a-cookie")
    def test_29_stale_version_fails_even_with_fresh_credential(self):
        r=self.receipt()
        self.ledger.correct(replace(self.event,evidence_id="SYN-EV-002"),expected_version=1)
        fresh=self.ace.issue_fixture(
            grant_id="SYN-GRANT-002",subject=PAT,grantee=READER,purpose=P,
            issued_at="2026-11-20T00:00:00+08:00",valid_until="2026-12-02T00:00:00+08:00")
        with self.assertRaises(HandoffRejected):
            self.inspect(r,token=fresh)
    def test_30_exposed_api_does_not_exist(self):
        from pathlib import Path
        code=Path("server.py").read_text()
        self.assertNotIn("/api/handoff",code)
        self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",code)


if __name__=="__main__": unittest.main()
