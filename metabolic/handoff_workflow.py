"""Build32 synthetic-only, segregated handoff workflow and audit.

Does NOT authenticate humans or connect to ACE/PAIR. Role identities are
test fixtures. No HTTP endpoints, external delivery or patient data.
"""
from __future__ import annotations

from dataclasses import dataclass, replace, asdict
from hashlib import sha256
import json
import re
import secrets
from typing import Literal

from .evidence_handoff import SyntheticHandoffService, HandoffRejected
from .longitudinal_memory import AccessDenied, IntegrityError

ACTOR = re.compile(r"^SYN-[A-Z0-9-]{3,48}$")
VALID_REASONS = frozenset({"INSUFFICIENT_EVIDENCE", "PURPOSE_MISMATCH", "REVIEW_DECLINED", "CANCEL_REQUESTED"})
ROLES = frozenset({"proposer", "reviewer", "executor", "recipient"})
TERMINAL = frozenset({"REJECTED", "CANCELLED", "EXECUTED"})


def _sha(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


class WorkflowDenied(PermissionError):
    pass


@dataclass(frozen=True)
class WorkflowCase:
    case_id: str
    event_id: str
    subject: str
    recipient: str
    proposer: str
    proposed_at: str
    state: str = "PROPOSED"
    reviewer: str | None = None
    executor: str | None = None
    approved_version: int | None = None
    approved_hash: str | None = None
    approved_tip: str | None = None
    receipt_id: str | None = None
    reason_code: str | None = None


@dataclass(frozen=True)
class AuditEntry:
    seq: int
    case_id: str
    actor: str
    event: str
    outcome: str
    reason: str
    previous_hash: str
    content_hash: str

    def digest(self) -> str:
        data = asdict(self)
        data.pop("content_hash")
        return _sha(data)


class SyntheticWorkflow:
    """Fail-closed synthetic approval/workflow state machine.

    Actor IDs and role assignments are mock fixtures; a caller with the
    Python object can impersonate an actor. This is not an identity service.
    """
    def __init__(self, *, handoff: SyntheticHandoffService, role_assignments: dict[str, str]):
        if not isinstance(handoff, SyntheticHandoffService):
            raise TypeError("HANDOFF_REQUIRED")
        if (not isinstance(role_assignments, dict)
                or not role_assignments
                or any(not isinstance(identity, str) or not ACTOR.fullmatch(identity)
                       or role not in ROLES for identity, role in role_assignments.items())):
            raise ValueError("SYNTHETIC_ROLES_REQUIRED")
        self._handoff = handoff
        self._roles = dict(role_assignments)
        self._cases: dict[str, WorkflowCase] = {}
        self._audit: list[AuditEntry] = []

    def _record(self, case_id: str, actor: str, event: str, outcome: str, reason: str = "NONE"):
        self.verify_audit()
        previous = self._audit[-1].content_hash if self._audit else "GENESIS"
        draft = AuditEntry(len(self._audit) + 1, case_id, actor, event, outcome, reason, previous, "")
        self._audit.append(replace(draft, content_hash=draft.digest()))

    def verify_audit(self) -> bool:
        previous = "GENESIS"
        for index, entry in enumerate(self._audit, 1):
            if entry.seq != index or entry.previous_hash != previous or entry.digest() != entry.content_hash:
                raise IntegrityError("WORKFLOW_AUDIT_CHAIN_INVALID")
            previous = entry.content_hash
        return True

    def _require(self, actor: str, role: str, case_id: str, action: str):
        if self._roles.get(actor) != role:
            self._record(case_id, actor if isinstance(actor, str) else "INVALID", action, "DENY", "ROLE_DENIED")
            raise WorkflowDenied("ROLE_DENIED")

    def _case(self, case_id: str) -> WorkflowCase:
        case = self._cases.get(case_id)
        if case is None:
            raise WorkflowDenied("UNKNOWN_CASE")
        return case

    def _save(self, case: WorkflowCase):
        self._cases[case.case_id] = case

    def propose(self, *, actor: str, event_id: str, subject: str, recipient: str, at: str) -> str:
        self._require(actor, "proposer", "SYN-CASE-REQUEST", "PROPOSE")
        if (not all(isinstance(s, str) and ACTOR.fullmatch(s) for s in (event_id, subject, recipient))
                or subject != self._handoff._owner_subject or self._roles.get(recipient) != "recipient"):
            self._record("SYN-CASE-REQUEST", actor, "PROPOSE", "DENY", "INVALID_SCOPE")
            raise WorkflowDenied("INVALID_SCOPE")
        case_id = "SYN-CASE-" + secrets.token_hex(8).upper()
        self._save(WorkflowCase(case_id, event_id, subject, recipient, actor, at))
        self._record(case_id, actor, "PROPOSE", "ALLOW")
        return case_id

    def review(self, *, actor: str, case_id: str, approve: bool, reason: str = "REVIEW_DECLINED") -> WorkflowCase:
        self._require(actor, "reviewer", case_id, "REVIEW")
        case = self._case(case_id)
        if case.state != "PROPOSED" or actor in (case.proposer, case.recipient):
            self._record(case_id, actor, "REVIEW", "DENY", "STATE_OR_SOD_DENIED")
            raise WorkflowDenied("STATE_OR_SOD_DENIED")
        if not approve:
            if reason not in VALID_REASONS:
                self._record(case_id, actor, "REVIEW", "DENY", "INVALID_REASON")
                raise WorkflowDenied("INVALID_REASON")
            result=replace(case,state="REJECTED",reviewer=actor,reason_code=reason)
            self._save(result)
            self._record(case_id, actor, "REVIEW", "REJECT", reason)
            return result
        # Approval is based on CURRENT synthetic evidence, but not on real medical review.
        self._handoff._ledger.verify_integrity()
        history=tuple(e for e in self._handoff._ledger._revisions if e.event_id == case.event_id)
        if not history or history[-1].action == "retract":
            self._record(case_id, actor, "REVIEW", "DENY", "EVIDENCE_UNAVAILABLE")
            raise WorkflowDenied("EVIDENCE_UNAVAILABLE")
        last=history[-1]
        result=replace(case,state="APPROVED",reviewer=actor,
                       approved_version=last.version,approved_hash=last.content_hash,
                       approved_tip=self._handoff._ledger._revisions[-1].content_hash)
        self._save(result)
        self._record(case_id,actor,"REVIEW","ALLOW")
        return result

    def cancel(self, *, actor: str, case_id: str) -> WorkflowCase:
        self._require(actor,"proposer",case_id,"CANCEL")
        case=self._case(case_id)
        if case.proposer != actor or case.state not in ("PROPOSED","APPROVED"):
            self._record(case_id,actor,"CANCEL","DENY","STATE_OR_OWNER_DENIED")
            raise WorkflowDenied("STATE_OR_OWNER_DENIED")
        result=replace(case,state="CANCELLED",reason_code="CANCEL_REQUESTED")
        self._save(result)
        self._record(case_id,actor,"CANCEL","ALLOW","CANCEL_REQUESTED")
        return result

    def execute(self, *, actor: str, case_id: str, token: object, at: str) -> str:
        self._require(actor,"executor",case_id,"EXECUTE")
        case=self._case(case_id)
        if case.state != "APPROVED" or actor in (case.proposer,case.reviewer,case.recipient):
            self._record(case_id,actor,"EXECUTE","DENY","STATE_OR_SOD_DENIED")
            raise WorkflowDenied("STATE_OR_SOD_DENIED")
        ledger=self._handoff._ledger
        ledger.verify_integrity()
        history=tuple(e for e in ledger._revisions if e.event_id == case.event_id)
        if (not history or history[-1].action == "retract"
                or history[-1].version != case.approved_version
                or history[-1].content_hash != case.approved_hash
                or not ledger._revisions or ledger._revisions[-1].content_hash != case.approved_tip):
            self._record(case_id,actor,"EXECUTE","DENY","STALE_EVIDENCE")
            raise WorkflowDenied("STALE_EVIDENCE")
        # Build31 checks owner, ACE-like consent, current evidence and chain tip.
        try:
            receipt=self._handoff.issue_receipt(token=token,subject=case.subject,
                      grantee=case.recipient,purpose="care_demo_review",at=at,
                      event_id=case.event_id)
        except (AccessDenied,HandoffRejected,IntegrityError):
            self._record(case_id,actor,"EXECUTE","DENY","CONSENT_OR_EVIDENCE_DENIED")
            raise
        result=replace(case,state="EXECUTED",executor=actor,receipt_id=receipt.receipt_id)
        self._save(result)
        self._record(case_id,actor,"EXECUTE","ALLOW")
        return receipt.receipt_id

    def inspect_for_recipient(self, *, actor: str, case_id: str, token: object, at: str):
        self._require(actor,"recipient",case_id,"INSPECT")
        case=self._case(case_id)
        if case.state != "EXECUTED" or case.recipient != actor or not case.receipt_id:
            self._record(case_id,actor,"INSPECT","DENY","STATE_OR_RECIPIENT_DENIED")
            raise WorkflowDenied("STATE_OR_RECIPIENT_DENIED")
        try:
            result=self._handoff.inspect(receipt_id=case.receipt_id,token=token,subject=case.subject,
                  grantee=case.recipient,purpose="care_demo_review",at=at)
        except (AccessDenied,HandoffRejected,IntegrityError):
            self._record(case_id,actor,"INSPECT","DENY","CONSENT_OR_EVIDENCE_DENIED")
            raise
        self._record(case_id,actor,"INSPECT","ALLOW")
        return result

    def audit_for_reviewer(self, *, actor: str) -> tuple[AuditEntry, ...]:
        self._require(actor,"reviewer","SYN-AUDIT-REQUEST","AUDIT")
        self.verify_audit()
        return tuple(self._audit)

    def status(self, *, actor: str, case_id: str) -> str:
        case=self._case(case_id)
        if actor not in (case.proposer, case.reviewer, case.executor, case.recipient):
            raise WorkflowDenied("ROLE_DENIED")
        # No observation data is returned.
        return case.state
