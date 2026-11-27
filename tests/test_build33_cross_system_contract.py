"""Build33 synthetic AI Missy / ACE / PAIR contract validation."""
import unittest
from dataclasses import replace
from metabolic.consent_contract import SyntheticAceContract
from metabolic.longitudinal_memory import Observation,SyntheticMemoryLedger
from metabolic.evidence_handoff import SyntheticHandoffService
from metabolic.handoff_workflow import SyntheticWorkflow
from metabolic.cross_system_contract import CrossSystemSimulator,PairFixture,ContractRequest,SCHEMA

AT="2026-11-27T13:00:00+08:00"
SUB="SYN-PATIENT-001";P="SYN-PROPOSER-001";R="SYN-REVIEWER-001"
X="SYN-EXECUTOR-001";N="SYN-RECIPIENT-001"
class CrossSystemBuild33(unittest.TestCase):
 def setUp(self):
  self.ace=SyntheticAceContract(testing_key=b"synthetic-cross-system-key-0123456789abcdef")
  self.ledger=SyntheticMemoryLedger(authorization=self.ace)
  self.obs=Observation("SYN-GL-001","glucose","check_in","2026-11-20T09:00:00+08:00",
    "2026-11-20T09:05:00+08:00","synthetic_patient_demo","SYN-EV-001")
  self.ledger.create(self.obs)
  self.handoff=SyntheticHandoffService(ledger=self.ledger,owner_subject=SUB)
  self.workflow=SyntheticWorkflow(handoff=self.handoff,
        role_assignments={P:"proposer",R:"reviewer",X:"executor",N:"recipient"})
  self.pair=PairFixture()
  self.service=CrossSystemSimulator(workflow=self.workflow,pair=self.pair)
  self.grant=self.ace.issue_fixture(grant_id="SYN-GRANT-001",subject=SUB,grantee=N,
      purpose="care_demo_review",issued_at="2026-11-01T00:00:00+08:00",
      valid_until="2026-12-01T00:00:00+08:00")
  self.case=self.workflow.propose(actor=P,event_id=self.obs.event_id,
      subject=SUB,recipient=N,at=AT)
  self.workflow.review(actor=R,case_id=self.case,approve=True)
  self.request=ContractRequest(SCHEMA,self.case,SUB,N,X,self.obs.event_id,
      "care_demo_review",AT,"SYN-IDEM-001A")
 def submit(self,request=None,token=None):
  return self.service.submit(request or self.request,token=self.grant if token is None else token)
 def test_01_happy_path_ack_has_matching_evidence(self):
  result=self.submit()
  self.assertEqual(result.status,"ACKNOWLEDGED")
  self.assertEqual(result.code,"ACCEPTED")
  self.assertTrue(result.pair_ack.startswith("SYN-PAIR-ACK-"))
  self.assertEqual(result.evidence_hash,self.ledger._revisions[-1].content_hash)
 def test_02_identical_retry_is_idempotent(self):
  first=self.submit();second=self.submit()
  self.assertEqual(first.receipt_id,second.receipt_id)
  self.assertEqual(first.pair_ack,second.pair_ack)
  self.assertEqual(second.code,"IDEMPOTENT")
  self.assertEqual(len(self.handoff._receipts),1)
 def test_03_pair_offline_pending_not_false_success(self):
  self.pair.set_online(False)
  result=self.submit()
  self.assertEqual(result.status,"PENDING")
  self.assertEqual(result.code,"PAIR_UNAVAILABLE")
  self.assertIsNone(result.pair_ack)
  self.assertEqual(len(self.handoff._receipts),1)
 def test_04_retry_after_outage_preserves_receipt(self):
  self.pair.set_online(False)
  first=self.submit()
  self.pair.set_online(True)
  second=self.submit()
  self.assertEqual(second.status,"ACKNOWLEDGED")
  self.assertEqual(first.receipt_id,second.receipt_id)
  self.assertEqual(len(self.handoff._receipts),1)
 def test_05_key_reuse_with_changed_scope_denied(self):
  self.submit()
  result=self.submit(replace(self.request,recipient="SYN-RECIPIENT-002"))
  self.assertEqual(result.code,"NOT_AUTHORIZED")
 def test_06_different_key_after_success_conflict(self):
  self.submit()
  result=self.submit(replace(self.request,idempotency_key="SYN-IDEM-002A"))
  self.assertEqual(result.code,"CONFLICT")
 def test_07_different_key_during_outage_conflict(self):
  self.pair.set_online(False);self.submit()
  result=self.submit(replace(self.request,idempotency_key="SYN-IDEM-002A"))
  self.assertEqual(result.code,"CONFLICT")
 def test_08_wrong_schema_denied(self):
  result=self.submit(replace(self.request,schema="live.v1"))
  self.assertEqual(result.code,"BAD_CONTRACT")
 def test_09_real_mode_denied(self):
  result=self.submit(replace(self.request,synthetic=False))
  self.assertEqual(result.code,"BAD_CONTRACT")
 def test_10_missing_actor_denied(self):
  result=self.submit(replace(self.request,executor="SYN-UNKNOWN-001"))
  self.assertEqual(result.code,"NOT_AUTHORIZED")
 def test_11_wrong_subject_denied(self):
  result=self.submit(replace(self.request,subject="SYN-PATIENT-002"))
  self.assertEqual(result.code,"NOT_AUTHORIZED")
 def test_12_wrong_event_denied(self):
  result=self.submit(replace(self.request,observed_event="SYN-BP-001"))
  self.assertEqual(result.code,"NOT_AUTHORIZED")
 def test_13_bad_idempotency_key_denied(self):
  result=self.submit(replace(self.request,idempotency_key="../path"))
  self.assertEqual(result.code,"BAD_CONTRACT")
 def test_14_revoked_before_execution_denied(self):
  self.ace.revoke(self.grant.grant_id)
  result=self.submit()
  self.assertEqual(result.code,"NOT_AUTHORIZED")
  self.assertEqual(len(self.handoff._receipts),0)
 def test_15_revoked_after_ack_replay_denied(self):
  first=self.submit()
  self.ace.revoke(self.grant.grant_id)
  second=self.submit()
  self.assertEqual(first.status,"ACKNOWLEDGED")
  self.assertEqual(second.code,"NOT_AUTHORIZED")
  self.assertIsNone(second.receipt_id)
 def test_16_stale_evidence_before_execution_denied(self):
  self.ledger.correct(replace(self.obs,evidence_id="SYN-EV-002"),expected_version=1)
  self.assertEqual(self.submit().code,"NOT_AUTHORIZED")
 def test_17_stale_evidence_after_ack_denied(self):
  self.submit()
  self.ledger.correct(replace(self.obs,evidence_id="SYN-EV-002"),expected_version=1)
  self.assertEqual(self.submit().code,"REPLAY_BLOCKED")
 def test_18_revoked_during_pending_prevents_ack(self):
  self.pair.set_online(False);self.submit()
  self.pair.set_online(True);self.ace.revoke(self.grant.grant_id)
  self.assertEqual(self.submit().code,"NOT_AUTHORIZED")
  self.assertEqual(len(self.pair._seen),0)
 def test_19_retracted_during_pending_prevents_ack(self):
  self.pair.set_online(False);self.submit()
  self.ledger.retract(self.obs.event_id,expected_version=1)
  self.pair.set_online(True)
  self.assertEqual(self.submit().code,"REPLAY_BLOCKED")
 def test_20_unknown_case_denied(self):
  result=self.submit(replace(self.request,case_id="SYN-CASE-0000000000000000"))
  self.assertEqual(result.code,"UNKNOWN_CASE")
 def test_21_cancelled_workflow_denied(self):
  other=self.workflow.propose(actor=P,event_id=self.obs.event_id,subject=SUB,recipient=N,at=AT)
  self.workflow.cancel(actor=P,case_id=other)
  r=replace(self.request,case_id=other)
  self.assertEqual(self.submit(r).code,"STATE_DENIED")
 def test_22_rejected_workflow_denied(self):
  other=self.workflow.propose(actor=P,event_id=self.obs.event_id,subject=SUB,recipient=N,at=AT)
  self.workflow.review(actor=R,case_id=other,approve=False)
  self.assertEqual(self.submit(replace(self.request,case_id=other)).code,"STATE_DENIED")
 def test_23_no_new_patient_http_route(self):
  from pathlib import Path
  src=Path("server.py").read_text()
  self.assertNotIn("/api/handoff",src)
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",src)
 def test_24_no_actual_transport_persistence_or_clinical_claim(self):
  from pathlib import Path
  src=Path("metabolic/cross_system_contract.py").read_text()
  self.assertNotIn("requests.",src)
  self.assertNotIn("urlopen(",src)
  self.assertNotIn("sqlite3.",src)
  self.assertNotIn("patient_record",src)
 def test_25_audit_denials_are_recorded(self):
  self.submit(replace(self.request,synthetic=False))
  self.submit()
  self.assertTrue(any(e[1]=="DENY" for e in self.service.audit()))
  self.assertTrue(any(e[1]=="ALLOW" for e in self.service.audit()))

if __name__=="__main__": unittest.main()
