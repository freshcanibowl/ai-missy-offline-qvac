"""Build33: isolated AI Missy -> ACE-like -> PAIR-like contract simulator.

This is an in-process fixture adapter, NOT verified ACE/PAIR API schema.
No HTTP transport, FHIR, hospital records, persistence or clinical decisions.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import re

from .handoff_workflow import SyntheticWorkflow, WorkflowDenied
from .longitudinal_memory import AccessDenied, IntegrityError
from .evidence_handoff import HandoffRejected

CASE_ID=re.compile(r"^SYN-CASE-[A-F0-9]{16}$")
KEY=re.compile(r"^SYN-IDEM-[A-Z0-9-]{4,48}$")
ENTITY=re.compile(r"^SYN-[A-Z0-9-]{3,48}$")
SCHEMA="missy-ace-pair-synthetic.v1"
ERRORS=frozenset({"BAD_CONTRACT","NOT_AUTHORIZED","STALE_EVIDENCE",
                  "CONFLICT","STATE_DENIED","INTEGRITY_FAILURE","UNKNOWN_CASE",
                  "REPLAY_BLOCKED"})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
            separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ContractRequest:
    schema: str
    case_id: str
    subject: str
    recipient: str
    executor: str
    observed_event: str
    purpose: str
    at: str
    idempotency_key: str
    synthetic: bool = True


@dataclass(frozen=True)
class ContractResult:
    schema: str
    status: str
    code: str
    receipt_id: str | None = None
    evidence_hash: str | None = None
    pair_ack: str | None = None
    synthetic: bool = True


class PairFixture:
    """Simulates receiving a handoff reference, never transmits data."""
    def __init__(self):
        self._seen={}
        self._online=True
    def set_online(self, online: bool):
        self._online=online
    def acknowledge(self, *, case_id: str, receipt_id: str,
                    evidence_hash: str, recipient: str) -> str:
        if not self._online:
            raise ConnectionError("PAIR_FIXTURE_OFFLINE")
        manifest={"case_id":case_id,"receipt_id":receipt_id,
                  "evidence_hash":evidence_hash,"recipient":recipient}
        if case_id in self._seen and self._seen[case_id] != manifest:
            raise ValueError("PAIR_ACK_CONFLICT")
        self._seen[case_id]=manifest
        return "SYN-PAIR-ACK-"+digest(manifest)[:20].upper()


class CrossSystemSimulator:
    """Fail-closed handoff with input contract checks and bounded retries.

    The caller supplies an already approved Build32 case. Receipt issuance is
    still governed by Build30 consent and Build31 evidence validation.
    """
    def __init__(self, *, workflow: SyntheticWorkflow, pair: PairFixture):
        if not isinstance(workflow,SyntheticWorkflow) or not isinstance(pair,PairFixture):
            raise TypeError("SYNTHETIC_ADAPTERS_REQUIRED")
        self.workflow=workflow
        self.pair=pair
        self._completed={}
        self._keys={}
        self._pending={}
        self._audit=[]

    def _log(self, request, outcome, code):
        self._audit.append((request.case_id if isinstance(request,ContractRequest) else "INVALID",
                            outcome,code))
    def audit(self):
        return tuple(self._audit)

    def _validate(self, r):
        if not isinstance(r,ContractRequest) or r.schema!=SCHEMA or r.synthetic is not True:
            return False
        if not isinstance(r.case_id,str) or not CASE_ID.fullmatch(r.case_id):
            return False
        if not isinstance(r.idempotency_key,str) or not KEY.fullmatch(r.idempotency_key):
            return False
        if not all(isinstance(v,str) and ENTITY.fullmatch(v) for v in
                   (r.subject,r.recipient,r.executor,r.observed_event)):
            return False
        return r.purpose=="care_demo_review" and isinstance(r.at,str) and r.at.endswith("+08:00")

    def _failure(self, r,code):
        if code not in ERRORS:
            raise ValueError("INVALID_ERROR_MAPPING")
        self._log(r,"DENY",code)
        return ContractResult(SCHEMA,"DENIED",code)

    def submit(self, request: ContractRequest, *, token: object):
        r=request
        if not self._validate(r):
            return self._failure(r,"BAD_CONTRACT")
        try:
            case=self.workflow._case(r.case_id)
        except WorkflowDenied:
            return self._failure(r,"UNKNOWN_CASE")
        # Matching case scope must be enforced even for already-completed requests.
        if (case.subject!=r.subject or case.recipient!=r.recipient or
                case.event_id!=r.observed_event or self.workflow._roles.get(r.executor)!="executor"):
            return self._failure(r,"NOT_AUTHORIZED")
        fp=digest({"schema":r.schema,"case_id":r.case_id,"subject":r.subject,
                   "recipient":r.recipient,"executor":r.executor,
                   "observed_event":r.observed_event,"purpose":r.purpose})
        existing=self._keys.get(r.idempotency_key)
        if existing is not None and existing!=(r.case_id,fp):
            return self._failure(r,"CONFLICT")

        # Consent re-check is required even for an idempotent response.
        ace=self.workflow._handoff._ledger._authorization
        if not ace.permit(token=token,subject=r.subject,grantee=r.recipient,
                          purpose=r.purpose,scope="timeline:read",at=r.at):
            return self._failure(r,"NOT_AUTHORIZED")
        try:
            self.workflow._handoff._ledger.verify_integrity()
            self.workflow.verify_audit()
        except IntegrityError:
            return self._failure(r,"INTEGRITY_FAILURE")

        if r.case_id in self._completed:
            if existing!=(r.case_id,fp):
                return self._failure(r,"CONFLICT")
            receipt,ack,proof=self._completed[r.case_id]
            try:
                preview=self.workflow.inspect_for_recipient(
                    actor=r.recipient,case_id=r.case_id,token=token,at=r.at)
            except (AccessDenied,HandoffRejected,IntegrityError,WorkflowDenied):
                return self._failure(r,"REPLAY_BLOCKED")
            if preview.revision_hash!=proof:
                return self._failure(r,"REPLAY_BLOCKED")
            self._log(r,"ALLOW","IDEMPOTENT")
            return ContractResult(SCHEMA,"ACKNOWLEDGED","IDEMPOTENT",receipt,proof,ack)

        if r.case_id in self._pending:
            if existing!=(r.case_id,fp):
                return self._failure(r,"CONFLICT")
            receipt,proof=self._pending[r.case_id]
            try:
                preview=self.workflow.inspect_for_recipient(
                    actor=r.recipient,case_id=r.case_id,token=token,at=r.at)
            except (AccessDenied,HandoffRejected,IntegrityError,WorkflowDenied):
                return self._failure(r,"REPLAY_BLOCKED")
            if preview.revision_hash!=proof:
                return self._failure(r,"REPLAY_BLOCKED")
        else:
            if case.state!="APPROVED":
                return self._failure(r,"STATE_DENIED")
            # Bind key before execution. A transient PAIR outage must not
            # permit a second receipt to be issued by a new idempotency key.
            if r.case_id in (case_id for case_id,_ in self._keys.values()):
                return self._failure(r,"CONFLICT")
            try:
                receipt=self.workflow.execute(actor=r.executor,case_id=r.case_id,
                                               token=token,at=r.at)
                preview=self.workflow.inspect_for_recipient(
                    actor=r.recipient,case_id=r.case_id,token=token,at=r.at)
            except (AccessDenied,HandoffRejected,WorkflowDenied):
                return self._failure(r,"NOT_AUTHORIZED")
            except IntegrityError:
                return self._failure(r,"INTEGRITY_FAILURE")
            proof=preview.revision_hash
            self._keys[r.idempotency_key]=(r.case_id,fp)
            self._pending[r.case_id]=(receipt,proof)
        try:
            ack=self.pair.acknowledge(case_id=r.case_id,receipt_id=receipt,
                     evidence_hash=proof,recipient=r.recipient)
        except ConnectionError:
            self._log(r,"PENDING","PAIR_UNAVAILABLE")
            return ContractResult(SCHEMA,"PENDING","PAIR_UNAVAILABLE",receipt,proof)
        except ValueError:
            return self._failure(r,"CONFLICT")
        self._pending.pop(r.case_id,None)
        self._completed[r.case_id]=(receipt,ack,proof)
        self._log(r,"ALLOW","ACCEPTED")
        return ContractResult(SCHEMA,"ACKNOWLEDGED","ACCEPTED",receipt,proof,ack)
