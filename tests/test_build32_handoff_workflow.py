"""Build32 synthetic-only role separation and audit negative tests."""
import unittest
from dataclasses import replace
from metabolic.consent_contract import SyntheticAceContract
from metabolic.longitudinal_memory import Observation,SyntheticMemoryLedger,AccessDenied,IntegrityError
from metabolic.evidence_handoff import SyntheticHandoffService,HandoffRejected
from metabolic.handoff_workflow import SyntheticWorkflow,WorkflowDenied

AT="2026-11-27T13:00:00+08:00"
P="SYN-PATIENT-001"
A="SYN-PROPOSER-001"
R="SYN-REVIEWER-001"
X="SYN-EXECUTOR-001"
N="SYN-RECIPIENT-001"
OTHER="SYN-OTHER-001"

class HandoffWorkflowBuild32(unittest.TestCase):
 def setUp(self):
  self.ace=SyntheticAceContract(testing_key=b"synthetic-workflow-testing-key-0123456789abcdef")
  self.ledger=SyntheticMemoryLedger(authorization=self.ace)
  self.obs=Observation("SYN-GL-001","glucose","check_in","2026-11-20T09:00:00+08:00",
     "2026-11-20T09:04:00+08:00","synthetic_patient_demo","SYN-EV-001")
  self.ledger.create(self.obs)
  self.handoff=SyntheticHandoffService(ledger=self.ledger,owner_subject=P)
  self.workflow=SyntheticWorkflow(handoff=self.handoff,role_assignments={
      A:"proposer",R:"reviewer",X:"executor",N:"recipient",OTHER:"proposer"})
  self.token=self.ace.issue_fixture(grant_id="SYN-GRANT-001",subject=P,grantee=N,
    purpose="care_demo_review",issued_at="2026-11-01T00:00:00+08:00",
    valid_until="2026-12-01T00:00:00+08:00")
 def propose(self):
  return self.workflow.propose(actor=A,event_id=self.obs.event_id,subject=P,recipient=N,at=AT)
 def approve(self,c):
  return self.workflow.review(actor=R,case_id=c,approve=True)
 def execute(self,c,**kw):
  return self.workflow.execute(actor=X,case_id=c,token=kw.get("token",self.token),at=kw.get("at",AT))
 def flow(self):
  c=self.propose();self.approve(c);receipt=self.execute(c);return c,receipt
 def inspect(self,c,**kw):
  return self.workflow.inspect_for_recipient(actor=N,case_id=c,token=kw.get("token",self.token),at=kw.get("at",AT))
 def test_01_complete_handoff(self):
  c,receipt=self.flow()
  self.assertTrue(receipt.startswith("SYN-HANDOFF-"))
  self.assertEqual(self.inspect(c).confirmation,"unverified")
  self.assertEqual(self.workflow.status(actor=A,case_id=c),"EXECUTED")
 def test_02_role_separation(self):
  c=self.propose()
  with self.assertRaises(WorkflowDenied):self.workflow.review(actor=A,case_id=c,approve=True)
  self.approve(c)
  with self.assertRaises(WorkflowDenied):self.workflow.execute(actor=R,case_id=c,token=self.token,at=AT)
  self.execute(c)
 def test_03_execute_before_review_denied(self):
  with self.assertRaises(WorkflowDenied):self.execute(self.propose())
 def test_04_reject_terminal_with_reason(self):
  c=self.propose()
  self.assertEqual(self.workflow.review(actor=R,case_id=c,approve=False,reason="INSUFFICIENT_EVIDENCE").state,"REJECTED")
  with self.assertRaises(WorkflowDenied):self.execute(c)
  self.assertTrue(any(e.reason=="INSUFFICIENT_EVIDENCE" for e in self.workflow.audit_for_reviewer(actor=R)))
 def test_05_invalid_reason_denied(self):
  c=self.propose()
  with self.assertRaises(WorkflowDenied):self.workflow.review(actor=R,case_id=c,approve=False,reason="patient-text")
 def test_06_review_replay_denied(self):
  c=self.propose();self.approve(c)
  with self.assertRaises(WorkflowDenied):self.approve(c)
 def test_07_execute_replay_denied(self):
  c,_=self.flow()
  with self.assertRaises(WorkflowDenied):self.execute(c)
 def test_08_cancel_before_approval(self):
  c=self.propose();self.assertEqual(self.workflow.cancel(actor=A,case_id=c).state,"CANCELLED")
  with self.assertRaises(WorkflowDenied):self.approve(c)
 def test_09_cancel_after_approval(self):
  c=self.propose();self.approve(c)
  self.workflow.cancel(actor=A,case_id=c)
  with self.assertRaises(WorkflowDenied):self.execute(c)
 def test_10_cancel_after_execution_denied(self):
  c,_=self.flow()
  with self.assertRaises(WorkflowDenied):self.workflow.cancel(actor=A,case_id=c)
 def test_11_other_proposer_cannot_cancel(self):
  c=self.propose()
  with self.assertRaises(WorkflowDenied):self.workflow.cancel(actor=OTHER,case_id=c)
 def test_12_revoke_before_execute_denied(self):
  c=self.propose();self.approve(c);self.ace.revoke(self.token.grant_id)
  with self.assertRaises(AccessDenied):self.execute(c)
 def test_13_revoke_after_execute_denied(self):
  c,_=self.flow();self.ace.revoke(self.token.grant_id)
  with self.assertRaises(AccessDenied):self.inspect(c)
 def test_14_correct_after_approval_denied(self):
  c=self.propose();self.approve(c)
  self.ledger.correct(replace(self.obs,evidence_id="SYN-EV-002"),expected_version=1)
  with self.assertRaises(WorkflowDenied):self.execute(c)
 def test_15_unrelated_change_invalidates_approval(self):
  c=self.propose();self.approve(c)
  self.ledger.create(replace(self.obs,event_id="SYN-BP-001",module="pressure",event="review"))
  with self.assertRaises(WorkflowDenied):self.execute(c)
 def test_16_retraction_prevents_approval(self):
  c=self.propose();self.ledger.retract(self.obs.event_id,expected_version=1)
  with self.assertRaises(WorkflowDenied):self.approve(c)
 def test_17_retraction_after_execution_denied(self):
  c,_=self.flow();self.ledger.retract(self.obs.event_id,expected_version=1)
  with self.assertRaises(HandoffRejected):self.inspect(c)
 def test_18_wrong_recipient_role_denied(self):
  c,_=self.flow()
  with self.assertRaises(WorkflowDenied):
   self.workflow.inspect_for_recipient(actor=A,case_id=c,token=self.token,at=AT)
 def test_19_inspect_before_execute_denied(self):
  with self.assertRaises(WorkflowDenied):self.inspect(self.propose())
 def test_20_audit_not_readable_by_proposer(self):
  self.propose()
  with self.assertRaises(WorkflowDenied):self.workflow.audit_for_reviewer(actor=A)
 def test_21_audit_records_allow_and_deny(self):
  c=self.propose()
  with self.assertRaises(WorkflowDenied):self.execute(c)
  self.approve(c);self.execute(c)
  events=self.workflow.audit_for_reviewer(actor=R)
  self.assertTrue(self.workflow.verify_audit())
  self.assertTrue(any(e.outcome=="DENY" for e in events))
  self.assertTrue(any(e.event=="EXECUTE" and e.outcome=="ALLOW" for e in events))
 def test_22_audit_content_tampering_detected(self):
  c=self.propose()
  self.workflow._audit[0]=replace(self.workflow._audit[0],outcome="REJECT")
  with self.assertRaises(IntegrityError):self.workflow.verify_audit()
  with self.assertRaises(IntegrityError):self.approve(c)
 def test_23_audit_link_tampering_detected(self):
  c=self.propose();self.approve(c)
  self.workflow._audit[1]=replace(self.workflow._audit[1],previous_hash="bad")
  with self.assertRaises(IntegrityError):self.workflow.verify_audit()
 def test_24_cross_subject_denied(self):
  with self.assertRaises(WorkflowDenied):
   self.workflow.propose(actor=A,event_id=self.obs.event_id,subject="SYN-PATIENT-002",recipient=N,at=AT)
 def test_25_unknown_recipient_denied(self):
  with self.assertRaises(WorkflowDenied):
   self.workflow.propose(actor=A,event_id=self.obs.event_id,subject=P,recipient="SYN-UNKNOWN-001",at=AT)
 def test_26_unknown_actor_denied(self):
  with self.assertRaises(WorkflowDenied):
   self.workflow.propose(actor="SYN-HACKER-001",event_id=self.obs.event_id,subject=P,recipient=N,at=AT)
 def test_27_unrelated_role_cannot_view_status(self):
  c=self.propose()
  with self.assertRaises(WorkflowDenied):self.workflow.status(actor=OTHER,case_id=c)
 def test_28_non_synthetic_role_denied(self):
  with self.assertRaises(ValueError):
   SyntheticWorkflow(handoff=self.handoff,role_assignments={"real-person":"reviewer"})
 def test_29_no_live_handoff_http_endpoint(self):
  from pathlib import Path
  code=Path("server.py").read_text()
  self.assertNotIn("/api/handoff",code)
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",code)
 def test_30_approval_is_not_clinical_confirmation(self):
  c=self.propose();self.approve(c)
  self.assertEqual(self.obs.confirmation,"unverified")
  self.assertEqual(self.workflow.status(actor=A,case_id=c),"APPROVED")

if __name__=="__main__":unittest.main()
