# Build 24 — Synthetic Identity → Ownership → Consent → Audit Decision Gate

Date: 2026-11-09. Development branch only. Main and PAIR production unchanged.

## What is implemented
- `metabolic/synthetic_decision_engine.py`: an in-memory SQLite fixture performing ownership, scoped consent, preview and minimal audit updates in one lock-protected transaction.
- `tests/test_build24_decision_engine.py`: 20 tests for missing authority, cross-user access/write, inappropriate purpose, revocation, replay after revocation, audit absence of identifiers and lock ordering.
- Every preview explicitly marks `synthetic=true`, `transfer_status=NOT_SENT`, `permission_to_transfer=false`, `clinical_review=REQUIRED`.

## Independent red-team blockers
- **Fixture principals are trivially forgeable.** A Python caller can construct `SyntheticPrincipal`; therefore this does NOT represent real verified identity.
- The Build23 OAuth adapter is a separate non-integrated component with no real identity provider. Merely passing a dataclass from it is not a secure identity boundary.
- No actual HTTP integration. `server.py` retains the hard denial of all `/api/metabolic/*` routes (403). Do not lift this deny-all on the basis of these tests.
- The audit is test-only, in-memory, not tamper-evident, and stores no account identifiers. It cannot serve forensic compliance needs or persist on restart.
- Revocation checks happen before every fixture preview, but a response already disclosed before revocation cannot be recalled. The tests do not prove distributed concurrency safety.
- No encryption, verified patient binding, consent expiry / signed grant, production authorization enforcement, real patient data, clinical approval, PAIR transfer or Windows QVAC evidence.
- Synthetic usability walkthrough and browser-only UI remain separate.

## Go / Stop
GO: isolated decision logic regression on the feature branch if GitHub CI succeeds.
HOLD: real identity provider, record storage, trustworthy audit, authenticated HTTP access, Windows offline proof.
NO-GO: any real clinical use or production release.

## Next substantive integration gate
Provision a supported identity-provider sandbox under explicit configuration; verify access tokens server-side and validate record ownership and current consent inside the data-access boundary. Test cross-account requests and immediate revocation over actual HTTP, fail closed when IDP unavailable. Never use the local synthetic bearer token as clinical identity.
