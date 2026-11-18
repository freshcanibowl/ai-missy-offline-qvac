import threading
import unittest
from metabolic.synthetic_decision_engine import SyntheticDecisionEngine,SyntheticPrincipal,AuthorizationDenied
A=SyntheticPrincipal("SYNTH_ALICE",frozenset(["fixture:read","fixture:write","fixture:consent"]))
B=SyntheticPrincipal("SYNTH_BOB",frozenset(["fixture:read","fixture:write"]))
R=SyntheticPrincipal("SYNTH_REVIEWER",frozenset(["fixture:review"]))
class TestBuild24DecisionEngine(unittest.TestCase):
 def setUp(self):
  self.e=SyntheticDecisionEngine()
  self.e.add(A,owner=A.subject)
 def tearDown(self):self.e.close()
 def denied(self,fn):
  with self.assertRaises(AuthorizationDenied):fn()
 def test_own_read(self):self.assertEqual(self.e.own_records(A,owner=A.subject),[("blood_pressure","SAMPLE_A")])
 def test_cross_read(self):self.denied(lambda:self.e.own_records(B,owner=A.subject))
 def test_cross_write(self):self.denied(lambda:self.e.add(B,owner=A.subject))
 def test_no_free_text(self):self.denied(lambda:self.e.add(A,owner=A.subject,sample="Patient 123"))
 def test_scope_deny(self):self.denied(lambda:self.e.own_records(R,owner=R.subject))
 def test_claimed_identity_dict_denied(self):self.denied(lambda:self.e.own_records({"subject":A.subject},owner=A.subject))
 def test_consent_required(self):self.denied(lambda:self.e.preview(R,owner=A.subject))
 def test_grant_then_preview(self):
  self.e.consent(A,grantee=R.subject,active=True)
  p=self.e.preview(R,owner=A.subject)
  self.assertEqual(p["transfer_status"],"NOT_SENT")
  self.assertFalse(p["permission_to_transfer"])
  self.assertEqual(p["items"],[("blood_pressure","SAMPLE_A")])
 def test_revoke_denies_replay(self):
  self.e.consent(A,grantee=R.subject,active=True)
  self.e.preview(R,owner=A.subject)
  self.e.consent(A,grantee=R.subject,active=False)
  for _ in range(3):self.denied(lambda:self.e.preview(R,owner=A.subject))
 def test_grant_wrong_purpose(self):self.denied(lambda:self.e.consent(A,grantee=R.subject,purpose="share_all",active=True))
 def test_purpose_escalation(self):
  self.e.consent(A,grantee=R.subject,active=True)
  self.denied(lambda:self.e.preview(R,owner=A.subject,purpose="export"))
 def test_consent_not_self_grant(self):self.denied(lambda:self.e.consent(A,grantee=A.subject,active=True))
 def test_consent_owner_scope(self):self.denied(lambda:self.e.consent(B,grantee=R.subject,active=True)) 
 def test_cross_subject_review(self):
  self.e.consent(A,grantee=R.subject,active=True)
  self.denied(lambda:self.e.preview(R,owner=B.subject))
 def test_audit_allows_and_denials(self):
  self.denied(lambda:self.e.own_records(B,owner=A.subject))
  events=self.e.audit_events()
  self.assertTrue(any(a=="own" and d=="DENY" for a,d,r in events))
  self.assertTrue(any(a=="add" and d=="ALLOW" for a,d,r in events))
 def test_audit_contains_no_subject_or_samples(self):
  self.denied(lambda:self.e.own_records(B,owner=A.subject))
  serialized=str(self.e.audit_events())
  for text in (A.subject,B.subject,R.subject,"SAMPLE_A"):
   self.assertNotIn(text,serialized)
 def test_regrant_after_revocation_is_explicit(self):
  self.e.consent(A,grantee=R.subject,active=True)
  self.e.consent(A,grantee=R.subject,active=False)
  self.denied(lambda:self.e.preview(R,owner=A.subject))
  self.e.consent(A,grantee=R.subject,active=True)
  self.assertEqual(self.e.preview(R,owner=A.subject)["clinical_review"],"REQUIRED")
 def test_atomic_revocation_orders_access(self):
  self.e.consent(A,grantee=R.subject,active=True)
  barrier=threading.Barrier(2)
  result=[]
  def revoke():
   barrier.wait();self.e.consent(A,grantee=R.subject,active=False)
  worker=threading.Thread(target=revoke)
  worker.start();barrier.wait();worker.join(timeout=3)
  self.assertFalse(worker.is_alive())
  self.denied(lambda:self.e.preview(R,owner=A.subject))
 def test_no_real_identity_provider_is_connected(self):
  from pathlib import Path
  code=(Path(__file__).resolve().parents[1]/"server.py").read_text()
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",code)
  self.assertIn("path.startswith('/api/metabolic/')",code)
 def test_invalid_consent_boolean(self):self.denied(lambda:self.e.consent(A,grantee=R.subject,active=1))
if __name__=="__main__":unittest.main()
