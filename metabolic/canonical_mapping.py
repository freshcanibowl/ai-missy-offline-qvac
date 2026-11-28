"""Build35: fail-closed canonical *synthetic* mapping research adapter.

Source snapshots (read 2026-11-28):
 ACE packages/contracts-schema/src/index.js at d582ecdce22f3c85d0023a41574535fc079ce31d
 PAIR web/intake.js at f57c2d9fa7fa56bf5524d08840e73ee939859716
 PAIR web/missy.js at 0fe60c5a6e591fd39924b18f3c149b605967e546

This is neither a validated wire adapter nor clinical software. The upstream
JS modules are NOT imported into this Python runtime; independent cross-repo
execution remains HOLD. No network, no patient identifiers, no real readings.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import re
from typing import Mapping

from .longitudinal_memory import Observation

class MappingDenied(ValueError):
    """Input cannot be represented without losing critical assurance."""

PAIR_ORDER=("review_context","prompt_medical_review","urgent_professional_assessment")
ACE_ORDER=("no_action","monitor","prompt_medical_review","urgent_review")
# A deliberate proposed CONSERVATIVE policy, not an ACE-approved clinical rule.
PROPOSED_PAIR_TO_ACE={
    "review_context":"monitor",
    "prompt_medical_review":"prompt_medical_review",
    "urgent_professional_assessment":"urgent_review",
}
SOURCE_CODES={"creatinine","egfr","potassium","sodium","urea","systolic_bp","diastolic_bp","weight"}
UNITS={"creatinine":{"mg/dL","umol/L"},"egfr":{"mL/min/1.73m2"},
       "potassium":{"mmol/L"},"sodium":{"mmol/L"},"urea":{"mmol/L"},
       "systolic_bp":{"mmHg"},"diastolic_bp":{"mmHg"},"weight":{"kg"}}
SYN_ID=re.compile(r"^SYN-[A-Z0-9-]{3,48}$")
# These are explicitly synthetic preview codes. Do not use with real patient data.


def proposed_escalation_map(pair_state: str, *, confirmed_by_rule_engine: bool) -> str:
    """No LLM can change the deterministic PAIR escalation state."""
    if confirmed_by_rule_engine is not True or pair_state not in PROPOSED_PAIR_TO_ACE:
        raise MappingDenied("PAIR_DETERMINISTIC_AUTHORITY_NOT_VERIFIED")
    result=PROPOSED_PAIR_TO_ACE[pair_state]
    if ACE_ORDER.index(result)<PAIR_ORDER.index(pair_state):
        raise MappingDenied("ESCALATION_DOWNGRADE_FORBIDDEN")
    return result


def verify_escalation_response(*, pair_state: str, ace_state: str,
                               explanation_pair_state: str,
                               confirmed_by_rule_engine: bool) -> bool:
    expected=proposed_escalation_map(pair_state,confirmed_by_rule_engine=confirmed_by_rule_engine)
    if ace_state!=expected or explanation_pair_state!=pair_state:
        raise MappingDenied("ESCALATION_STATE_TAMPER_OR_DOWNGRADE")
    return True


@dataclass(frozen=True)
class SyntheticMeasurement:
    code: str
    value: float
    unit: str
    confidence: float
    source_id: str


@dataclass(frozen=True)
class SyntheticExtraction:
    schema: str
    document_id: str
    captured_at: str
    subject: str
    declared_deidentified: bool
    identifiers_retained: tuple[str,...]
    agent_role: str
    clinical_inference_performed: bool
    human_confirmed: bool
    confirmed_by: str
    measurements: tuple[SyntheticMeasurement,...]
    synthetic: bool=True


def _id(value: object) -> bool:
    return isinstance(value,str) and bool(SYN_ID.fullmatch(value))


def _timestamp(value: object) -> bool:
    from datetime import datetime
    if not isinstance(value,str) or not value.endswith("+08:00"):return False
    try:
        d=datetime.fromisoformat(value)
        return d.utcoffset() is not None and d.utcoffset().total_seconds()==28800
    except (ValueError,TypeError):
        return False


def prepare_pair_intake_preview(data: SyntheticExtraction, *,
                                expected_subject: str,
                                authorization_verified: bool) -> dict:
    """Construct in-memory fixture only; does not invoke PAIR, ACE or emit HTTP."""
    if not isinstance(data,SyntheticExtraction) or data.synthetic is not True:
        raise MappingDenied("SYNTHETIC_ONLY")
    if (not _id(expected_subject) or not _id(data.subject)
            or data.subject!=expected_subject or authorization_verified is not True):
        raise MappingDenied("SUBJECT_OR_AUTHORIZATION_UNVERIFIED")
    if (data.schema!="missy.synthetic-extraction.v1"
            or not _id(data.document_id) or not _timestamp(data.captured_at)):
        raise MappingDenied("EXTRACTION_CONTRACT_INVALID")
    if (data.declared_deidentified is not True or data.identifiers_retained
            or data.agent_role!="extract_and_normalize_only"
            or data.clinical_inference_performed is not False):
        raise MappingDenied("PRIVACY_OR_EXTRACTION_ROLE_UNSAFE")
    if not (data.human_confirmed is True and _id(data.confirmed_by)):
        raise MappingDenied("EXPLICIT_HUMAN_CONFIRMATION_REQUIRED")
    if not isinstance(data.measurements,tuple) or not data.measurements:
        raise MappingDenied("MEASUREMENTS_MISSING")
    seen=set()
    records=[]
    for m in data.measurements:
        if not isinstance(m,SyntheticMeasurement) or m.code not in SOURCE_CODES:
            raise MappingDenied("UNSUPPORTED_MEASUREMENT")
        if m.code in seen:
            raise MappingDenied("DUPLICATE_MEASUREMENT_CODE")
        seen.add(m.code)
        if (not isinstance(m.value,(float,int)) or isinstance(m.value,bool)
                or not math.isfinite(m.value) or m.value<=0):
            raise MappingDenied("INVALID_MEASUREMENT_VALUE")
        if m.unit not in UNITS[m.code]:
            raise MappingDenied("UNIT_UNKNOWN_OR_UNVERIFIED")
        if (not isinstance(m.confidence,(float,int))
                or isinstance(m.confidence,bool)
                or not math.isfinite(m.confidence)
                or not 0.95<=m.confidence<=1):
            raise MappingDenied("CONFIDENCE_REQUIRES_REVIEW")
        if not _id(m.source_id):
            raise MappingDenied("PROVENANCE_MISSING")
        records.append({"code":m.code,"value":float(m.value),"unit":m.unit,
                        "confidence":float(m.confidence),"evidence_ref":m.source_id})
    if "creatinine" not in seen:
        raise MappingDenied("CREATININE_REQUIRED_FOR_PAIR_CASE")
    # PAIR web/intake.js validates the following fields. This Python function
    # is stricter in some places and remains unconfirmed by live JS execution.
    return {
        "schema_version":"pair.renal-intake.v1",
        "privacy":{"deidentified":True,"identifiers_retained":[]},
        "document":{"source_id":data.document_id,"captured_at":data.captured_at},
        "extraction":{"agent_role":"extract_and_normalize_only",
                      "clinical_inference_performed":False,
                      "human_confirmation_required":False},
        "measurements":records,
        "synthetic":True,
        "assurance":{"human_confirmed":True,"confirmed_by":data.confirmed_by,
                     "release_gate":"NO_GO","target":"offline_fixture_only"}
    }


def refuse_unverified_observation(observation: Observation) -> None:
    """Build29/30 task observations are NEVER clinical lab measurements."""
    if not isinstance(observation,Observation):
        raise MappingDenied("INVALID_OBSERVATION")
    observation.validate()
    raise MappingDenied("UNVERIFIED_OBSERVATION_HAS_NO_MEASUREMENT_VALUE")


def refuse_ace_edge_capture_without_wire_contract(*args,**kwargs) -> None:
    """ACE's draft tagged type is NOT a verified online ingestion service."""
    raise MappingDenied("ACE_EDGE_CAPTURE_WIRE_CONFORMANCE_NOT_VERIFIED")
