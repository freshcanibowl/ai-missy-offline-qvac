"""Build30: synthetic-only append-only longitudinal memory integrity.

NOT a database, clinical store, authentication service or live ACE integration.
No HTTP routes, persistence, patient measurements or health advice.
"""
from __future__ import annotations
import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Literal


MODULES = frozenset({"glucose", "pressure", "renal", "lipids"})
EVENTS = frozenset({"review", "check_in", "follow_up", "lab_review"})
SOURCES = frozenset({"synthetic_patient_demo", "synthetic_care_plan"})
ACTIONS = frozenset({"create", "correct", "retract"})
IDENTIFIER = re.compile(r"^SYN-[A-Z0-9-]{3,48}$")


class IntegrityError(ValueError):
    """A record, version chain or contract is invalid."""


class AccessDenied(PermissionError):
    """The separate ACE authorization contract did not approve access."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _date(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("+08:00"):
        raise IntegrityError("EXPLICIT_SYNTHETIC_TIMEZONE_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise IntegrityError("INVALID_SYNTHETIC_TIMESTAMP") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 28800:
        raise IntegrityError("SYNTHETIC_TIMEZONE_REJECTED")
    return parsed


@dataclass(frozen=True)
class Observation:
    event_id: str
    module: str
    event: str
    observed_at: str
    recorded_at: str
    source: str
    evidence_id: str
    confirmation: Literal["unverified"] = "unverified"
    scope: Literal["demo_only"] = "demo_only"
    synthetic: Literal[True] = True

    def validate(self) -> None:
        if (not isinstance(self.event_id, str) or not IDENTIFIER.fullmatch(self.event_id)
                or not isinstance(self.evidence_id, str) or not IDENTIFIER.fullmatch(self.evidence_id)):
            raise IntegrityError("SYNTHETIC_IDENTIFIER_REQUIRED")
        if self.module not in MODULES or self.event not in EVENTS or self.source not in SOURCES:
            raise IntegrityError("UNSUPPORTED_SYNTHETIC_DOMAIN")
        if self.confirmation != "unverified" or self.scope != "demo_only" or self.synthetic is not True:
            raise IntegrityError("REAL_OR_CONFIRMED_RECORD_REJECTED")
        if _date(self.observed_at) > _date(self.recorded_at):
            raise IntegrityError("OBSERVATION_AFTER_RECORDING")


@dataclass(frozen=True)
class Revision:
    position: int
    event_id: str
    version: int
    action: str
    observation: Observation
    previous_hash: str
    previous_event_hash: str
    content_hash: str

    def payload(self) -> dict:
        return {
            "position": self.position, "event_id": self.event_id,
            "version": self.version, "action": self.action,
            "observation": asdict(self.observation),
            "previous_hash": self.previous_hash,
            "previous_event_hash": self.previous_event_hash,
        }

    def recompute_hash(self) -> str:
        return hashlib.sha256(_canonical(self.payload())).hexdigest()


class SyntheticMemoryLedger:
    """In-memory, no I/O. All reads require an external authorization adapter."""

    def __init__(self, authorization=None):
        # Fail closed if nothing is injected. Never instantiate a mock authority in this class.
        from .consent_contract import DenyAllAce
        self._authorization = authorization if authorization is not None else DenyAllAce()
        self._revisions: list[Revision] = []

    def _latest(self, event_id: str) -> Revision | None:
        return next((entry for entry in reversed(self._revisions) if entry.event_id == event_id), None)

    def _append(self, action: str, observation: Observation, expected_version: int) -> Revision:
        observation.validate()
        if action not in ACTIONS:
            raise IntegrityError("INVALID_REVISION_ACTION")
        self.verify_integrity()
        previous = self._latest(observation.event_id)
        if previous is None:
            if action != "create" or expected_version != 0:
                raise IntegrityError("CREATE_FIRST_REQUIRED")
        else:
            if action == "create" or previous.action == "retract":
                raise IntegrityError("EVENT_CANNOT_BE_RECREATED")
            if previous.version != expected_version:
                raise IntegrityError("STALE_EXPECTED_VERSION")
            if previous.observation.module != observation.module:
                raise IntegrityError("MODULE_CANNOT_BE_REASSIGNED")
        version = 1 if previous is None else previous.version + 1
        revision = Revision(
            position=len(self._revisions) + 1,
            event_id=observation.event_id, version=version, action=action,
            observation=observation,
            previous_hash=self._revisions[-1].content_hash if self._revisions else "GENESIS",
            previous_event_hash=previous.content_hash if previous else "GENESIS",
            content_hash="",
        )
        revision = replace(revision, content_hash=revision.recompute_hash())
        self._revisions.append(revision)
        return revision

    def create(self, observation: Observation) -> Revision:
        return self._append("create", observation, 0)

    def correct(self, observation: Observation, *, expected_version: int) -> Revision:
        return self._append("correct", observation, expected_version)

    def retract(self, event_id: str, *, expected_version: int) -> Revision:
        self.verify_integrity()
        previous = self._latest(event_id)
        if previous is None:
            raise IntegrityError("UNKNOWN_EVENT")
        return self._append("retract", previous.observation, expected_version)

    def verify_integrity(self) -> bool:
        previous_hash = "GENESIS"
        latest: dict[str, Revision] = {}
        for index, entry in enumerate(self._revisions, start=1):
            entry.observation.validate()
            previous_event = latest.get(entry.event_id)
            expected_version = 1 if previous_event is None else previous_event.version + 1
            expected_action = "create" if previous_event is None else None
            if (entry.position != index or entry.event_id != entry.observation.event_id
                    or entry.version != expected_version or entry.action not in ACTIONS
                    or (expected_action is not None and entry.action != expected_action)
                    or (previous_event is not None and (entry.action == "create" or previous_event.action == "retract"
                       or entry.observation.module != previous_event.observation.module))
                    or entry.previous_hash != previous_hash
                    or entry.previous_event_hash != (previous_event.content_hash if previous_event else "GENESIS")
                    or entry.content_hash != entry.recompute_hash()):
                raise IntegrityError("CHAIN_INTEGRITY_FAILURE")
            latest[entry.event_id] = entry
            previous_hash = entry.content_hash
        return True

    def read_history(self, *, token: object, subject: str, grantee: str,
                     purpose: str, at: str, event_id: str | None = None) -> tuple[Revision, ...]:
        # Always validate *before* returning any data (including event existence).
        self.verify_integrity()
        if not self._authorization.permit(token=token, subject=subject, grantee=grantee,
                                          purpose=purpose, at=at, scope="timeline:read"):
            raise AccessDenied("ACE_CONSENT_UNAVAILABLE")
        if event_id is not None:
            return tuple(e for e in self._revisions if e.event_id == event_id)
        return tuple(self._revisions)

    def read_active(self, *, token: object, subject: str, grantee: str,
                    purpose: str, at: str) -> tuple[Observation, ...]:
        revisions = self.read_history(token=token, subject=subject, grantee=grantee, purpose=purpose, at=at)
        latest = {entry.event_id: entry for entry in revisions}
        return tuple(entry.observation for entry in latest.values() if entry.action != "retract")
