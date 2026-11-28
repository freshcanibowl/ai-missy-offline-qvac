# Build 23 — OAuth Token Introspection Boundary

2026-11-09. Development branch only; PR #5 draft.

## Implementation
`metabolic/introspection_gate.py` validates the prerequisites for issuing a *verified identity claim*: HTTPS-configured introspection, authenticated client secret, opaque bearer-token format, active state, exact issuer, audience, subject, expiry, not-before and required scope. Default transport uses system TLS, bounded response and rejects HTTP redirects. Synthetic negative tests inject a fake transport, without any live identity-provider requests.

**No identity provider is connected or configured. No actual patient account exists.** A `VerifiedIdentity` object is just a Python dataclass and is forgeable by code with module access; it is NOT a trusted privilege object across process or HTTP boundaries. This adapter is not connected to the main HTTP server. Even a verified OAuth access token would still need authoritative patient-to-record ownership, scoped consent, revocation, audit and storage authorization. `test_only_no_patient_access` intentionally refuses those privileges.

## Threat model / conditions
- Treat provider config as trusted server-only secrets, not user input. Store client secret securely outside source, rotate it and limit scope.
- Server must not accept caller-supplied `sub`, `aud`, verified flags or consent claims.
- Validate introspection results against a preapproved issuer, audience and required scope on every sensitive request; account for cache/revocation freshness.
- Never equate identity verification with consent or authorization. Never use synthetic fixture principals as production identities.
- Keep `/api/metabolic/*` blocked (HTTP 403) until the complete authorization enforcement and audit is integrated and independently validated.
- No real health data, no live OAuth credentials, no production deployment and no changes to PAIR main.

## Gates
**GO:** static adapter and negative tests on development branch (subject to CI result).
**HOLD:** production identity-provider selection and actual introspection + per-request subject ownership and consent + negative cross-user HTTP tests.
**NO-GO:** real patient data, medication / clinical targets, automatic PAIR transfers and release.
