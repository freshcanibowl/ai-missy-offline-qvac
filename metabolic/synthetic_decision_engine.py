"""Build24 synthetic-only decision engine.

The verifier is injected ONLY by tests; a production provider does NOT exist.
Do not call from server.py or use with real medical data.
"""
import sqlite3
import threading
from dataclasses import dataclass
from metabolic.introspection_gate import VerifiedIdentity

class AuthorizationDenied(PermissionError):
    pass

@dataclass(frozen=True)
class SyntheticPrincipal:
    # Deliberately forgeable: fixture principal, not production authentication.
    subject: str
    scopes: frozenset[str]

class SyntheticDecisionEngine:
    """Transaction-scoped consent, ownership and audit fixture.

    Revocation and preview acquire the same reentrant lock, giving a
    total order. An already returned preview cannot be 'unsent' by revoke.
    """
    def __init__(self):
        self.db=sqlite3.connect(":memory:",check_same_thread=False,isolation_level=None)
        self.lock=threading.RLock()
        self.db.executescript("""
            CREATE TABLE records(id INTEGER PRIMARY KEY,owner TEXT NOT NULL,kind TEXT NOT NULL,sample TEXT NOT NULL);
            CREATE TABLE consent(owner TEXT NOT NULL, grantee TEXT NOT NULL,purpose TEXT NOT NULL,active INTEGER NOT NULL CHECK(active IN (0,1)),version INTEGER NOT NULL,PRIMARY KEY(owner,grantee,purpose));
            CREATE TABLE audit(seq INTEGER PRIMARY KEY AUTOINCREMENT,action TEXT NOT NULL, decision TEXT NOT NULL,reason TEXT NOT NULL);
        """)
    @staticmethod
    def _principal(value):
        if not isinstance(value,SyntheticPrincipal) or not isinstance(value.subject,str) or not 1<=len(value.subject)<=64 or value.subject.strip()!=value.subject:
            raise AuthorizationDenied("FIXTURE_PRINCIPAL_REQUIRED")
        if not isinstance(value.scopes,frozenset):raise AuthorizationDenied("SCOPES_INVALID")
        return value
    def _audit(self,action,decision,reason):
        self.db.execute("INSERT INTO audit(action,decision,reason) VALUES(?,?,?)",(action,decision,reason))
    def _run(self,action,principal,operation):
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                actor=self._principal(principal)
                value=operation(actor)
            except (AuthorizationDenied,ValueError,TypeError) as exc:
                self.db.execute("ROLLBACK")
                self.db.execute("BEGIN IMMEDIATE")
                self._audit(action,"DENY",getattr(exc,"args",["REJECTED"])[0] or "REJECTED")
                self.db.execute("COMMIT")
                raise
            except BaseException:
                self.db.execute("ROLLBACK")
                raise
            self._audit(action,"ALLOW","SYNTHETIC_FIXTURE_ONLY")
            self.db.execute("COMMIT")
            return value
    @staticmethod
    def _scope(actor,needed):
        if needed not in actor.scopes:raise AuthorizationDenied("SCOPE_DENIED")
    def add(self,actor,*,owner,kind="blood_pressure",sample="SAMPLE_A"):
        def op(a):
            self._scope(a,"fixture:write")
            if owner!=a.subject:raise AuthorizationDenied("CROSS_SUBJECT_WRITE")
            if kind not in ("blood_pressure","blood_glucose") or sample not in ("SAMPLE_A","SAMPLE_B"):
                raise AuthorizationDenied("SYNTHETIC_ONLY")
            return self.db.execute("INSERT INTO records(owner,kind,sample) VALUES(?,?,?)",(owner,kind,sample)).lastrowid
        return self._run("add",actor,op)
    def own_records(self,actor,*,owner):
        def op(a):
            self._scope(a,"fixture:read")
            if owner!=a.subject:raise AuthorizationDenied("CROSS_SUBJECT_READ")
            return self.db.execute("SELECT kind,sample FROM records WHERE owner=? ORDER BY id",(owner,)).fetchall()
        return self._run("own",actor,op)
    def consent(self,owner_actor,*,grantee,purpose="care_review",active):
        def op(a):
            self._scope(a,"fixture:consent")
            if not isinstance(active,bool) or purpose!="care_review" or not isinstance(grantee,str) or not grantee or grantee==a.subject:
                raise AuthorizationDenied("INVALID_CONSENT")
            self.db.execute("""INSERT INTO consent(owner,grantee,purpose,active,version) VALUES(?,?,?,?,1)
                ON CONFLICT(owner,grantee,purpose) DO UPDATE SET active=excluded.active,version=version+1""",(a.subject,grantee,purpose,int(active)))
            return True
        return self._run("consent",owner_actor,op)
    def preview(self,grantee_actor,*,owner,purpose="care_review"):
        def op(a):
            self._scope(a,"fixture:review")
            if purpose!="care_review" or a.subject==owner:raise AuthorizationDenied("PURPOSE_OR_SUBJECT_DENIED")
            consent=self.db.execute("SELECT active FROM consent WHERE owner=? AND grantee=? AND purpose=?",(owner,a.subject,purpose)).fetchone()
            if consent is None or consent[0]!=1:raise AuthorizationDenied("CONSENT_INACTIVE")
            rows=self.db.execute("SELECT kind,sample FROM records WHERE owner=? ORDER BY id",(owner,)).fetchall()
            return {"synthetic":True,"transfer_status":"NOT_SENT","permission_to_transfer":False,"clinical_review":"REQUIRED","items":rows}
        return self._run("preview",grantee_actor,op)
    def audit_events(self):
        with self.lock:
            # Strictly no subject, sample, token or patient ID in audit result.
            return self.db.execute("SELECT action,decision,reason FROM audit ORDER BY seq").fetchall()
    def close(self):
        with self.lock:self.db.close()
