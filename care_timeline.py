"""Build 23 — read-only synthetic care timeline.

This is a local, synthetic-only record browser. It does not establish
identity, consent, clinical provenance, or cryptographic integrity.
"""
import datetime
import uuid
from core import demo_plan

SCHEMA_VERSION = "ai-missy.synthetic-timeline.v1"
MAX_PAGE_SIZE = 50
MAX_OFFSET = 1000


def _valid_timestamp(value):
    if not isinstance(value, str):
        raise ValueError("TIMELINE_EVENT_INVALID")
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("TIMELINE_EVENT_INVALID") from exc
    if parsed.tzinfo is None:
        raise ValueError("TIMELINE_EVENT_INVALID")
    return value


def build_synthetic_timeline(conn, *, limit=20, offset=0):
    """Return a bounded page of confirmed local observations, newest first.

    Ordering is deterministic for a static database. Offset pagination is
    not a stable snapshot if concurrent new events are inserted.
    """
    plan = demo_plan()
    if type(limit) is not int or not 1 <= limit <= MAX_PAGE_SIZE:
        raise ValueError("INVALID_TIMELINE_LIMIT")
    if type(offset) is not int or not 0 <= offset <= MAX_OFFSET:
        raise ValueError("INVALID_TIMELINE_OFFSET")

    total = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    rows = conn.execute(
        "SELECT id, ml, confirmed_at FROM observations "
        "ORDER BY confirmed_at DESC, id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    events = []
    for row in rows:
        event_id, ml, confirmed_at = row["id"], row["ml"], row["confirmed_at"]
        try:
            uuid.UUID(event_id)
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError("TIMELINE_EVENT_INVALID") from exc
        if type(ml) is not int or not 1 <= ml <= 3000:
            raise ValueError("TIMELINE_EVENT_INVALID")
        events.append({
            "event_id": event_id,
            "event_type": "FLUID_INTAKE_RECORDED",
            "volume_ml": ml,
            "confirmed_at": _valid_timestamp(confirmed_at),
            "source_type": "locally_confirmed_record",
            "cryptographic_attestation": False,
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "synthetic": True,
        "plan_id": plan["plan"]["plan_id"],
        "page": {"limit": limit, "offset": offset, "total": total,
                 "has_more": offset + len(events) < total},
        "events": events,
        "disclaimer": (
            "Synthetic observations only; not a clinical record or "
            "a cryptographically verified provenance chain."
        ),
    }
