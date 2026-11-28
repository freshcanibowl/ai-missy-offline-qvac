"""Build30: fail-closed ACE-like contract for synthetic test fixtures ONLY.

Mock signature authenticates a *test* approval, not a patient, user or live ACE
approval. Never expose this module as a production authorization service.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

ID = re.compile(r"^SYN-[A-Z0-9-]{3,48}$")
IDENTITIES = re.compile(r"^SYN-[A-Z0-9-]{3,48}$")
PURPOSES = frozenset({"care_demo_review", "audit_demo"})
SCOPE = "timeline:read"


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _parse(value: str) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("+08:00"):
        return None
    try:
        date = datetime.fromisoformat(value)
    except ValueError:
        return None
    return date if date.utcoffset() is not None and date.utcoffset().total_seconds() == 28800 else None


@dataclass(frozen=True)
class SyntheticConsent:
    grant_id: str
    subject: str
    grantee: str
    purpose: str
    scope: str
    issued_at: str
    valid_until: str
    synthetic: bool
    approval_ref: str
    signature: str

    def signed_payload(self) -> dict:
        data = asdict(self)
        data.pop("signature")
        return data


class DenyAllAce:
    def permit(self, **kwargs) -> bool:
        return False


class SyntheticAceContract:
    """Test-only signing key simulates an external approval authority.

    The caller cannot self-grant permission through the memory ledger.
    Revocation is checked on every read; grants remain bounded in time.
    """
    def __init__(self, *, testing_key: bytes):
        if not isinstance(testing_key, bytes) or len(testing_key) < 32:
            raise ValueError("TEST_KEY_REQUIRED")
        self.__key = testing_key
        self.__revoked: set[str] = set()
        self.__registered: dict[str, SyntheticConsent] = {}

    def issue_fixture(self, *, grant_id: str, subject: str, grantee: str, purpose: str,
                      issued_at: str, valid_until: str) -> SyntheticConsent:
        # This method is a fixture builder and must never be a runtime user API.
        if (not all(isinstance(s, str) and ID.fullmatch(s) for s in (grant_id, subject, grantee))
                or purpose not in PURPOSES):
            raise ValueError("INVALID_SYNTHETIC_GRANT")
        issued = _parse(issued_at)
        valid = _parse(valid_until)
        if issued is None or valid is None or issued >= valid:
            raise ValueError("INVALID_CONSENT_INTERVAL")
        unsigned = SyntheticConsent(grant_id, subject, grantee, purpose, SCOPE,
                                    issued_at, valid_until, True, "SYN-ACE-APPROVAL", "")
        sig = hmac.new(self.__key, _canonical(unsigned.signed_payload()), hashlib.sha256).hexdigest()
        grant = SyntheticConsent(**{**unsigned.signed_payload(), "signature": sig})
        if grant_id in self.__registered:
            raise ValueError("GRANT_REPLAY_REJECTED")
        self.__registered[grant_id] = grant
        return grant

    def revoke(self, grant_id: str) -> bool:
        if grant_id not in self.__registered:
            return False
        self.__revoked.add(grant_id)
        return True

    def permit(self, *, token: object, subject: str, grantee: str,
               purpose: str, scope: str, at: str) -> bool:
        if not isinstance(token, SyntheticConsent) or token.grant_id in self.__revoked:
            return False
        registered = self.__registered.get(token.grant_id)
        if registered is None or not hmac.compare_digest(registered.signature, token.signature):
            return False
        signed = hmac.new(self.__key, _canonical(token.signed_payload()), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signed, token.signature):
            return False
        if token != registered:
            return False
        instant, start, end = _parse(at), _parse(token.issued_at), _parse(token.valid_until)
        return bool(
            instant is not None and start is not None and end is not None
            and start <= instant < end
            and token.synthetic is True and token.scope == SCOPE and scope == SCOPE
            and token.purpose in PURPOSES and purpose == token.purpose
            and token.subject == subject and token.grantee == grantee
            and isinstance(subject, str) and IDENTITIES.fullmatch(subject)
            and isinstance(grantee, str) and IDENTITIES.fullmatch(grantee)
            and token.approval_ref == "SYN-ACE-APPROVAL"
        )
