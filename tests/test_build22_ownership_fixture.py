"""Build22: synthetic only; never infer clinical authorization from these tests."""
import unittest
from metabolic.synthetic_ownership_fixture import FixtureActor,SyntheticAccessDenied,SyntheticJournal

class OwnershipFixtureTests(unittest.TestCase):
    def setUp(self):
        self.j=SyntheticJournal()
        self.alice=FixtureActor("SYNTHETIC_ALICE")
        self.bob=FixtureActor("SYNTHETIC_BOB")
        self.reviewer=FixtureActor("SYNTHETIC_REVIEWER")
        self.r=self.j.add(self.alice,owner_id=self.alice.actor_id,kind="blood_pressure",sample="SAMPLE_A",synthetic=True,confirmed=True)
    def tearDown(self):self.j.close()
    def test_owner_can_read_own_sample(self):
        rows=self.j.read_own(self.alice,owner_id=self.alice.actor_id)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][0],self.r)
    def test_cross_user_read_is_denied(self):
        with self.assertRaises(SyntheticAccessDenied):self.j.read_own(self.bob,owner_id=self.alice.actor_id)
    def test_cross_user_write_is_denied(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.add(self.bob,owner_id=self.alice.actor_id,kind="blood_pressure",sample="SAMPLE_A",synthetic=True,confirmed=True)
    def test_no_non_synthetic_values(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.add(self.alice,owner_id=self.alice.actor_id,kind="blood_pressure",sample="SAMPLE_A",synthetic=False,confirmed=True)
    def test_explicit_confirmation_required(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.add(self.alice,owner_id=self.alice.actor_id,kind="blood_pressure",sample="SAMPLE_A",synthetic=True,confirmed=False)
    def test_rejects_free_text(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.add(self.alice,owner_id=self.alice.actor_id,kind="food_habit",sample="person's phone number",synthetic=True,confirmed=True)
    def test_rejects_unknown_kind(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.add(self.alice,owner_id=self.alice.actor_id,kind="medication_order",sample="SAMPLE_A",synthetic=True,confirmed=True)
    def test_claimed_identity_dict_not_accepted(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.read_own({"actor_id":self.alice.actor_id,"verified":True},owner_id=self.alice.actor_id)
    def test_no_grant_means_no_preview(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.preview_for(self.reviewer,owner_id=self.alice.actor_id)
    def test_owner_must_grant_explicitly(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.grant_preview(self.alice,grantee_id=self.reviewer.actor_id,confirmed=False)
    def test_granted_preview_never_sends(self):
        self.j.grant_preview(self.alice,grantee_id=self.reviewer.actor_id,confirmed=True)
        x=self.j.preview_for(self.reviewer,owner_id=self.alice.actor_id)
        self.assertEqual(x["transfer_status"],"NOT_SENT")
        self.assertFalse(x["permission_to_transfer"])
        self.assertEqual(x["clinical_review"],"REQUIRED")
        self.assertEqual(len(x["items"]),1)
    def test_revoke_immediately_blocks_preview(self):
        self.j.grant_preview(self.alice,grantee_id=self.reviewer.actor_id,confirmed=True)
        self.j.revoke_preview(self.alice,grantee_id=self.reviewer.actor_id)
        with self.assertRaises(SyntheticAccessDenied):
            self.j.preview_for(self.reviewer,owner_id=self.alice.actor_id)
    def test_grant_does_not_authorize_other_subject(self):
        self.j.grant_preview(self.alice,grantee_id=self.reviewer.actor_id,confirmed=True)
        with self.assertRaises(SyntheticAccessDenied):
            self.j.preview_for(self.reviewer,owner_id=self.bob.actor_id)
    def test_grant_does_not_authorize_other_purpose(self):
        self.j.grant_preview(self.alice,grantee_id=self.reviewer.actor_id,confirmed=True)
        with self.assertRaises(SyntheticAccessDenied):
            self.j.preview_for(self.reviewer,owner_id=self.alice.actor_id,purpose="export")
    def test_cannot_self_grant_a_preview(self):
        with self.assertRaises(SyntheticAccessDenied):
            self.j.grant_preview(self.alice,grantee_id=self.alice.actor_id,confirmed=True)
    def test_bob_only_sees_bob_records(self):
        self.j.add(self.bob,owner_id=self.bob.actor_id,kind="blood_glucose",sample="SAMPLE_B",synthetic=True,confirmed=True)
        alice=self.j.read_own(self.alice,owner_id=self.alice.actor_id)
        bob=self.j.read_own(self.bob,owner_id=self.bob.actor_id)
        self.assertEqual([x[1] for x in alice],["blood_pressure"])
        self.assertEqual([x[1] for x in bob],["blood_glucose"])
    def test_revoke_does_not_erase_owner_record(self):
        self.j.grant_preview(self.alice,grantee_id=self.reviewer.actor_id,confirmed=True)
        self.j.revoke_preview(self.alice,grantee_id=self.reviewer.actor_id)
        self.assertEqual(len(self.j.read_own(self.alice,owner_id=self.alice.actor_id)),1)

if __name__=="__main__":unittest.main()
