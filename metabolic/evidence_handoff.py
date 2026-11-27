"""Build31: evidence-bound synthetic care handoff PREVIEW.

No real PAIR/ACE connection, no network transport, no persistence and no export.
A receipt is opaque. Inspection re-checks integrity, consent, current versions.
Reading a previously delivered preview cannot be clawed back after revocation.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import re
import secrets

from .longitudinal_memory import AccessDenied, IntegrityError, SyntheticMemoryLedger

HANDOFF_ID = re.compile(r"^SYN-HANDOFF-[A-F0-9]{24}$")
EVENT_ID = re.compile(r"^SYN-[A-Z0-9-]{3,48}$")
PURPOSE = "care_demo_review"


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


class HandoffRejected(RuntimeError):
    """No readable, current, authorized handoff can be created or inspected."""


@dataclass(frozen=True)
class HandoffReceipt:
    receipt_id: str
    event_id: str
    revision: int
    revision_hash: str
    chain_tip: str
    subject: str
    grantee: str
    purpose: str
    created_at: str
    manifest_hash: str


@dataclass(frozen=True)
class HandoffPreview:
    receipt_id: str
    event_id: str
    module: str
    action: str
    version: int
    observed_at: str
    recorded_at: str
    source: str
    evidence_id: str
    confirmation: str
    synthetic: bool
    scope: str
    revision_hash: str
    manifest_hash: str
    note: str = "SYNTHETIC_ONLY_NOT_CLINICAL_EVIDENCE"


class SyntheticHandoffService:
    """One-time creation + reauthorized, read-only inspection.

    The service deliberately does not issue credentials or grant consent.
    Rejects any change to the global chain after a receipt was created,
    even when the target observation itself was not edited.
    """
    def __init__(self, *, ledger: SyntheticMemoryLedger):
        if not isinstance(ledger, SyntheticMemoryLedger):
            raise TypeError("SYNTHETIC_LEDGER_REQUIRED")
        self._ledger = ledger
        self._receipts: dict[str, HandoffReceipt] = {}

    def _authorized_history(self, *, token: object, subject: str,
                            grantee: str, purpose: str, at: str,
                            event_id: str):
        if purpose != PURPOSE or not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
            raise HandoffRejected("HANDOFF_CONTRACT_REJECTED")
        return self._ledger.read_history(
            token=token, subject=subject, grantee=grantee,
            purpose=purpose, at=at, event_id=event_id
        )

    def issue_receipt(self, *, token: object, subject: str, grantee: str,
                      purpose: str, at: str, event_id: str) -> HandoffReceipt:
        history = self._authorized_history(token=token, subject=subject,
                                           grantee=grantee, purpose=purpose,
                                           at=at, event_id=event_id)
        if not history or history[-1].action == "retract":
            raise HandoffRejected("EVENT_NOT_ACTIVE")
        latest = history[-1]
        # Public receipt includes no observation content. Consistency with
        # entire ledger is checked again on inspection.
        tip = self._ledger._revisions[-1].content_hash
        receipt_id = "SYN-HANDOFF-" + secrets.token_hex(12).upper()
        manifest = {
            "receipt_id": receipt_id, "event_id": latest.event_id,
            "revision": latest.version, "revision_hash": latest.content_hash,
            "chain_tip": tip, "subject": subject, "grantee": grantee,
            "purpose": purpose, "created_at": at,
        }
        record = HandoffReceipt(**manifest, manifest_hash=sha256(_canonical(manifest)).hexdigest())
        self._receipts[receipt_id] = record
        return record

    def inspect(self, *, receipt_id: str, token: object, subject: str,
                grantee: str, purpose: str, at: str) -> HandoffPreview:
        if not isinstance(receipt_id, str) or not HANDOFF_ID.fullmatch(receipt_id):
            raise HandoffRejected("INVALID_RECEIPT")
        registered = self._receipts.get(receipt_id)
        # Avoid publishing event existence to unauthenticated requests.
        if registered is None:
            raise HandoffRejected("UNKNOWN_RECEIPT")
        history = self._authorized_history(token=token, subject=subject,
                                           grantee=grantee, purpose=purpose,
                                           at=at, event_id=registered.event_id)
        if registered.subject != subject or registered.grantee != grantee or registered.purpose != purpose:
            raise AccessDenied("HANDOFF_IDENTITY_SCOPE_DENIED")
        manifest = {
            "receipt_id": registered.receipt_id, "event_id": registered.event_id,
            "revision": registered.revision, "revision_hash": registered.revision_hash,
            "chain_tip": registered.chain_tip, "subject": registered.subject,
            "grantee": registered.grantee, "purpose": registered.purpose,
            "created_at": registered.created_at,
        }
        if sha256(_canonical(manifest)).hexdigest() != registered.manifest_hash:
            raise IntegrityError("HANDOFF_MANIFEST_MODIFIED")
        if (not history or history[-1].action == "retract"
                or history[-1].version != registered.revision
                or history[-1].content_hash != registered.revision_hash
                or not self._ledger._revisions
                or self._ledger._revisions[-1].content_hash != registered.chain_tip):
            raise HandoffRejected("HANDOFF_STALE_OR_RETRACTED")
        last = history[-1]
        observation = last.observation
        return HandoffPreview(
            receipt_id=receipt_id, event_id=observation.event_id,
            module=observation.module, action=last.action, version=last.version,
            observed_at=observation.observed_at, recorded_at=observation.recorded_at,
            source=observation.source, evidence_id=observation.evidence_id,
            confirmation=observation.confirmation, synthetic=observation.synthetic,
            scope=observation.scope, revision_hash=last.content_hash,
            manifest_hash=registered.manifest_hash
        )
