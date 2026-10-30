"""Build 22: synthetic-only, offline JSON care record export.

This is an interoperability experiment, not a medical record exchange format.
Never enable this for real patient data without authentication, consent,
encryption-at-rest, retention, and clinical/governance review.
"""
import datetime
from core import demo_plan

SCHEMA_VERSION = "ai-missy.synthetic-care.v1"
MAX_EXPORT_EVENTS = 1000


def build_synthetic_export(conn):
    """Export confirmed synthetic fluid events, excluding free-text and reminders."""
    plan = demo_plan()  # fail closed if demo fixture is not explicitly synthetic
    rows = conn.execute(
        "SELECT id, ml, confirmed_at FROM observations "
        "ORDER BY confirmed_at, id LIMIT ?", (MAX_EXPORT_EVENTS + 1,)
    ).fetchall()
    if len(rows) > MAX_EXPORT_EVENTS:
        raise ValueError("EXPORT_TOO_LARGE")
    events = []
    for row in rows:
        event_id, ml, confirmed_at = row["id"], row["ml"], row["confirmed_at"]
        if not isinstance(event_id, str) or type(ml) is not int or not 1 <= ml <= 3000:
            raise ValueError("EXPORT_EVENT_INVALID")
        if not isinstance(confirmed_at, str) or not confirmed_at:
            raise ValueError("EXPORT_EVENT_INVALID")
        events.append({
            "event_id": event_id,
            "volume_ml": ml,
            "confirmed_at": confirmed_at,
            "origin": "local-user-confirmed",
        })
    baseline = sum(
        item["volume_ml"] for item in plan["observations"]
        if item.get("confirmed_by_user") is True
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "synthetic": True,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "plan_id": plan["plan"]["plan_id"],
        "units": "mL",
        "baseline_recorded_ml": baseline,
        "confirmed_events": events,
        "recorded_total_ml": baseline + sum(e["volume_ml"] for e in events),
        "excludes": ["free_text", "reminder_titles", "patient_identifiers", "model_weights"],
        "disclaimer": "Synthetic prototype export only. Not a clinical record, diagnosis or prescribed fluid allowance.",
    }
