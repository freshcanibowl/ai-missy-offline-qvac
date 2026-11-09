"""Build22: *synthetic fixture only* for ownership and consent invariants.

NOT an identity provider, real authorization service, or HTTP integration.
A trusted backend must supply verified identity and binding before reuse.
Never use this class with real patient information.
"""
from dataclasses import dataclass
import sqlite3

class SyntheticAccessDenied(PermissionError):
    pass

@dataclass(frozen=True)
class FixtureActor:
    # Constructors are test fixtures; IDs are not trusted authentication.
    actor_id: str

class SyntheticJournal:
    """In-memory SQLite fixture demonstrating server-side ownership checks."""

    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE records (record_id INTEGER PRIMARY KEY, owner_id TEXT NOT NULL, kind TEXT NOT NULL, sample TEXT NOT NULL, synthetic INTEGER NOT NULL CHECK(synthetic=1))")
        self.db.execute("CREATE TABLE consent (owner_id TEXT NOT NULL, grantee_id TEXT NOT NULL, purpose TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)), PRIMARY KEY(owner_id,grantee_id,purpose))")
        self.db.commit()

    @staticmethod
    def _id(actor):
        if not isinstance(actor, FixtureActor) or not isinstance(actor.actor_id, str) or not actor.actor_id or len(actor.actor_id)>64:
            raise SyntheticAccessDenied("FIXTURE_ID_REQUIRED")
        return actor.actor_id

    def add(self, actor, *, owner_id, kind, sample, synthetic, confirmed):
        actor_id=self._id(actor)
        if actor_id!=owner_id: raise SyntheticAccessDenied("CROSS_SUBJECT_WRITE_DENIED")
        if synthetic is not True or confirmed is not True: raise SyntheticAccessDenied("SYNTHETIC_CONFIRMATION_REQUIRED")
        if kind not in ("blood_pressure","blood_glucose","daily_activity","food_habit"):
            raise SyntheticAccessDenied("KIND_DENIED")
        if sample not in ("SAMPLE_A","SAMPLE_B"): raise SyntheticAccessDenied("FREE_TEXT_DENIED")
        with self.db:
            row=self.db.execute("INSERT INTO records(owner_id,kind,sample,synthetic) VALUES (?,?,?,1)",(actor_id,kind,sample))
        return row.lastrowid

    def read_own(self, actor, *, owner_id):
        actor_id=self._id(actor)
        if actor_id!=owner_id: raise SyntheticAccessDenied("CROSS_SUBJECT_READ_DENIED")
        return self.db.execute("SELECT record_id,kind,sample FROM records WHERE owner_id=? ORDER BY record_id",(actor_id,)).fetchall()

    def grant_preview(self, owner, *, grantee_id, confirmed, purpose="care_review"):
        owner_id=self._id(owner)
        if not confirmed or not isinstance(grantee_id,str) or not grantee_id or grantee_id==owner_id:
            raise SyntheticAccessDenied("INVALID_SYNTHETIC_CONSENT")
        if purpose!="care_review": raise SyntheticAccessDenied("PURPOSE_DENIED")
        with self.db:
            self.db.execute("INSERT INTO consent(owner_id,grantee_id,purpose,active) VALUES(?,?,?,1) ON CONFLICT(owner_id,grantee_id,purpose) DO UPDATE SET active=1",(owner_id,grantee_id,purpose))

    def revoke_preview(self, owner, *, grantee_id):
        owner_id=self._id(owner)
        with self.db:
            self.db.execute("UPDATE consent SET active=0 WHERE owner_id=? AND grantee_id=? AND purpose='care_review'",(owner_id,grantee_id))

    def preview_for(self, actor, *, owner_id, purpose="care_review"):
        actor_id=self._id(actor)
        if purpose!="care_review" or actor_id==owner_id: raise SyntheticAccessDenied("PREVIEW_PURPOSE_DENIED")
        allowed=self.db.execute("SELECT active FROM consent WHERE owner_id=? AND grantee_id=? AND purpose=?",(owner_id,actor_id,purpose)).fetchone()
        if allowed is None or allowed[0]!=1: raise SyntheticAccessDenied("CONSENT_NOT_ACTIVE")
        rows=self.db.execute("SELECT kind,sample FROM records WHERE owner_id=? ORDER BY record_id",(owner_id,)).fetchall()
        return {"synthetic":True,"transfer_status":"NOT_SENT","permission_to_transfer":False,"clinical_review":"REQUIRED","items":rows}

    def close(self):
        self.db.close()
