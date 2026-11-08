"""Build16 fail-closed metabolic read gate. This is NOT patient authentication."""
from dataclasses import dataclass
class AccessDenied(PermissionError): pass
@dataclass(frozen=True)
class AccessDecision:
    actor_id: str
    subject_id: str
    purpose: str
    resource: str
    verified_identity: bool
    verified_consent: bool
    verified_subject_binding: bool
    from_trusted_enforcement_point: bool
_RESOURCES={'metabolic_entries','pair_preview'}
_PURPOSES={'view_own_records','patient_review_export'}
def authorize_read(decision: AccessDecision | None, *, expected_resource: str) -> None:
    if expected_resource not in _RESOURCES: raise AccessDenied('RESOURCE_NOT_ALLOWED')
    if not isinstance(decision,AccessDecision): raise AccessDenied('VERIFIED_IDENTITY_REQUIRED')
    if decision.resource!=expected_resource: raise AccessDenied('RESOURCE_MISMATCH')
    if not decision.actor_id or decision.actor_id!=decision.subject_id: raise AccessDenied('SUBJECT_BINDING_REQUIRED')
    if decision.purpose not in _PURPOSES: raise AccessDenied('PURPOSE_NOT_ALLOWED')
    if not all((decision.verified_identity,decision.verified_consent,decision.verified_subject_binding,decision.from_trusted_enforcement_point)):
        raise AccessDenied('TRUSTED_AUTHORIZATION_REQUIRED')
    # Caller-supplied claims are forgeable. Never grant without a real
    # verified identity + consent enforcement backend.
    raise AccessDenied('ENFORCEMENT_BACKEND_NOT_CONNECTED')
def read_policy_for_endpoint(path: str):
    return {'/api/metabolic/entries':'metabolic_entries','/api/metabolic/pair-preview':'pair_preview'}.get(path)
