"""Build30 independent synthetic-only memory & ACE contract tests.

Never use patient records, clinical values, external identity or live secrets.
"""
import unittest
from dataclasses import replace

from metabolic.longitudinal_memory import (
    AccessDenied, IntegrityError, Observation, SyntheticMemoryLedger,
)
from metabolic.consent_contract import SyntheticAceContract, SyntheticConsent


AT = "2026-11-27T10:00:00+08:00"
SUBJECT = "SYN-PATIENT-001"
GRANTEE = "SYN-REVIEWER-001"
PURPOSE = "care_demo_review"


def sample(event_id="SYN-GL-001", **changes):
    fields=dict(
        event_id=event_id, module="glucose", event="check_in",
        observed_at="2026-11-10T09:00:00+08:00",
        recorded_at="2026-11-10T09:05:00+08:00",
        source="synthetic_patient_demo", evidence_id="SYN-EV-102",
    )
    fields.update(changes)
    return Observation(**fields)


class SyntheticMemoryBuild30(unittest.TestCase):
    def setUp(self):
        self.authority=SyntheticAceContract(testing_key=b"test-only-not-a-production-key-0123456789abcdef")
        self.memory=SyntheticMemoryLedger(authorization=self.authority)
        self.observation=sample()
        self.grant=self.authority.issue_fixture(
            grant_id="SYN-GRANT-001", subject=SUBJECT, grantee=GRANTEE,
            purpose=PURPOSE, issued_at="2026-11-01T00:00:00+08:00",
            valid_until="2026-12-01T00:00:00+08:00",
        )
    def read(self, **overrides):
        args=dict(token=self.grant,subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,at=AT)
        args.update(overrides)
        return self.memory.read_history(**args)
    def test_01_sha256_deterministic_content_binding(self):
        r=self.memory.create(self.observation)
        self.assertEqual(len(r.content_hash),64)
        self.assertEqual(r.content_hash,r.recompute_hash())
        self.assertEqual(r.previous_hash,"GENESIS")
        self.assertTrue(self.memory.verify_integrity())
    def test_02_revision_chain_append_only_and_versioned(self):
        r1=self.memory.create(self.observation)
        revised=replace(self.observation,recorded_at="2026-11-11T09:00:00+08:00",evidence_id="SYN-EV-103")
        r2=self.memory.correct(revised,expected_version=1)
        self.assertEqual((r1.version,r2.version),(1,2))
        self.assertEqual(r2.previous_hash,r1.content_hash)
        self.assertEqual(r2.previous_event_hash,r1.content_hash)
        self.assertEqual([r.action for r in self.read()],["create","correct"])
    def test_03_retract_is_tombstone_not_deletion(self):
        self.memory.create(self.observation)
        tombstone=self.memory.retract(self.observation.event_id,expected_version=1)
        self.assertEqual(tombstone.action,"retract")
        self.assertEqual(len(self.read()),2)
        self.assertEqual(self.memory.read_active(token=self.grant,subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,at=AT),())
        with self.assertRaises(IntegrityError):
            self.memory.correct(self.observation,expected_version=2)
    def test_04_default_deny_without_authority(self):
        private=SyntheticMemoryLedger()
        private.create(self.observation)
        with self.assertRaises(AccessDenied):
            private.read_history(token=self.grant,subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,at=AT)
    def test_05_absent_grant_fails_closed(self):
        self.memory.create(self.observation)
        with self.assertRaises(AccessDenied):
            self.read(token=None)
    def test_06_revocation_invalidates_future_reads(self):
        self.memory.create(self.observation)
        self.assertEqual(len(self.read()),1)
        self.assertTrue(self.authority.revoke(self.grant.grant_id))
        with self.assertRaises(AccessDenied):
            self.read()
    def test_07_wrong_subject_and_cross_grantee_denied(self):
        self.memory.create(self.observation)
        for arg in (dict(subject="SYN-PATIENT-002"),dict(grantee="SYN-REVIEWER-002")):
            with self.subTest(arg=arg),self.assertRaises(AccessDenied):
                self.read(**arg)
    def test_08_wrong_purpose_and_scope_denied(self):
        self.memory.create(self.observation)
        with self.assertRaises(AccessDenied):
            self.read(purpose="audit_demo")
        self.assertFalse(self.authority.permit(token=self.grant,subject=SUBJECT,grantee=GRANTEE,
                          purpose=PURPOSE,scope="timeline:write",at=AT))
    def test_09_expired_and_not_yet_valid_denied(self):
        self.memory.create(self.observation)
        for instant in ("2026-10-31T23:59:59+08:00","2026-12-01T00:00:00+08:00"):
            with self.subTest(at=instant),self.assertRaises(AccessDenied):
                self.read(at=instant)
    def test_10_invalid_signature_or_tampered_scope_denied(self):
        self.memory.create(self.observation)
        for token in (replace(self.grant,signature="0"*64),
                      replace(self.grant,scope="timeline:write"),
                      replace(self.grant,subject="SYN-PATIENT-002")):
            with self.subTest(token=token),self.assertRaises(AccessDenied):
                self.read(token=token)
    def test_11_record_mutation_detected(self):
        self.memory.create(self.observation)
        self.memory._revisions[0]=replace(self.memory._revisions[0],observation=replace(self.observation,evidence_id="SYN-EV-666"))
        with self.assertRaises(IntegrityError):
            self.memory.verify_integrity()
        with self.assertRaises(IntegrityError):
            self.read()
    def test_12_version_chain_tampering_detected(self):
        self.memory.create(self.observation)
        self.memory.correct(replace(self.observation,evidence_id="SYN-EV-103"),expected_version=1)
        self.memory._revisions[1]=replace(self.memory._revisions[1],previous_event_hash="bad")
        with self.assertRaises(IntegrityError):
            self.memory.verify_integrity()
    def test_13_stale_write_and_duplicate_creation_rejected(self):
        self.memory.create(self.observation)
        with self.assertRaises(IntegrityError):
            self.memory.create(self.observation)
        with self.assertRaises(IntegrityError):
            self.memory.correct(self.observation,expected_version=0)
    def test_14_unknown_retract_and_cross_domain_correction_rejected(self):
        with self.assertRaises(IntegrityError):
            self.memory.retract("SYN-UNKNOWN",expected_version=1)
        self.memory.create(self.observation)
        with self.assertRaises(IntegrityError):
            self.memory.correct(replace(self.observation,module="renal"),expected_version=1)
    def test_15_real_or_confirmed_record_rejected(self):
        for changes in (dict(synthetic=False),dict(scope="patient_record"),dict(confirmation="confirmed"),
                        dict(event_id="patient-001"),dict(source="clinical_ehr")):
            with self.subTest(changes=changes),self.assertRaises(IntegrityError):
                self.memory.create(sample(**changes))
    def test_16_invalid_or_backdated_timestamp_rejected(self):
        for changes in (dict(observed_at="2026-11-10T09:00:00Z"),
                        dict(observed_at="2026-11-10T11:00:00+08:00",recorded_at="2026-11-10T09:00:00+08:00"),
                        dict(recorded_at="yesterday")):
            with self.subTest(changes=changes),self.assertRaises(IntegrityError):
                self.memory.create(sample(**changes))
    def test_17_grant_replay_and_purpose_input_rejected(self):
        with self.assertRaises(ValueError):
            self.authority.issue_fixture(grant_id=self.grant.grant_id,subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,
              issued_at="2026-11-01T00:00:00+08:00",valid_until="2026-12-01T00:00:00+08:00")
        with self.assertRaises(ValueError):
            self.authority.issue_fixture(grant_id="SYN-GRANT-002",subject=SUBJECT,grantee=GRANTEE,purpose="any-purpose",
              issued_at="2026-11-01T00:00:00+08:00",valid_until="2026-12-01T00:00:00+08:00")
    def test_18_revoked_grant_cannot_be_resurrected(self):
        self.memory.create(self.observation)
        self.authority.revoke(self.grant.grant_id)
        with self.assertRaises(AccessDenied):
            self.read()
        fresh=self.authority.issue_fixture(grant_id="SYN-GRANT-002",subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,
          issued_at="2026-11-20T00:00:00+08:00",valid_until="2026-12-02T00:00:00+08:00")
        self.assertEqual(len(self.read(token=fresh)),1)
        with self.assertRaises(AccessDenied):
            self.read()
    def test_19_revision_linkage_across_distinct_events(self):
        first=self.memory.create(self.observation)
        second=self.memory.create(sample("SYN-BP-001",module="pressure",event="review"))
        self.assertEqual(second.previous_hash,first.content_hash)
        self.assertEqual(second.previous_event_hash,"GENESIS")
        self.assertTrue(self.memory.verify_integrity())
    def test_20_returns_immutable_history_snapshot(self):
        self.memory.create(self.observation)
        result=self.read()
        self.assertIsInstance(result,tuple)
        with self.assertRaises((AttributeError,TypeError)):
            result[0].version=900
    def test_21_retraction_does_not_erase_provenance(self):
        self.memory.create(self.observation)
        self.memory.retract(self.observation.event_id,expected_version=1)
        self.assertEqual([x.observation.evidence_id for x in self.read()],["SYN-EV-102","SYN-EV-102"])
    def test_22_cannot_issue_unbounded_consent(self):
        with self.assertRaises(ValueError):
            self.authority.issue_fixture(grant_id="SYN-GRANT-003",subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,
              issued_at="2026-11-03T00:00:00+08:00",valid_until="2026-11-03T00:00:00+08:00")
    def test_23_consent_rejects_non_synthetic_identities(self):
        with self.assertRaises(ValueError):
            self.authority.issue_fixture(grant_id="SYN-GRANT-003",subject="patient-001",grantee=GRANTEE,purpose=PURPOSE,
              issued_at="2026-11-01T00:00:00+08:00",valid_until="2026-12-01T00:00:00+08:00")
    def test_24_read_history_filters_event_after_authorization(self):
        self.memory.create(self.observation)
        self.memory.create(sample("SYN-BP-001",module="pressure",event="review"))
        result=self.memory.read_history(token=self.grant,subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,at=AT,event_id="SYN-BP-001")
        self.assertEqual(len(result),1)
        self.assertEqual(result[0].event_id,"SYN-BP-001")
        with self.assertRaises(AccessDenied):
            self.memory.read_history(token=None,subject=SUBJECT,grantee=GRANTEE,purpose=PURPOSE,at=AT,event_id="SYN-BP-001")


if __name__=="__main__":
    unittest.main()
