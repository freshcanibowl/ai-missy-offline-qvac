# Build 22 — Synthetic Ownership and Consent Revocation Gate

Date: 2026-11-09. Branch: feature/daily-metabolic-care-build09 (Draft PR #5).

## Implemented
- `metabolic/synthetic_ownership_fixture.py`: disposable **in-memory SQLite fixture** with per-record owner IDs and explicit owner/grantee consent.
- `tests/test_build22_ownership_fixture.py`: 17 test scenarios including cross-user read/write, missing and withdrawn consent, denied exports and cross-subject access.
- Consent preview is **always** synthetic, `transfer_status=NOT_SENT`, `permission_to_transfer=false`, and `clinical_review=REQUIRED`.

## Security truth
FixtureActor is **NOT** a verified user identity. It may be constructed by arbitrary Python code, so it does not establish production authorization. The fixture must never be used as a real patient data store or be exposed through HTTP. It accepts only the exact sample markers SAMPLE_A and SAMPLE_B, no actual measurements or free text.

The actual `server.py` still rejects `/api/metabolic/*` GET and POST with 403. No connection from the fixture to live HTTP or the Windows QVAC path is implemented. In-memory data vanish at teardown. Main, PAIR production and release settings remain unchanged.

## Remaining gates before real daily care data
1. Choose a real identity provider and implement server-verified user subject binding and session invalidation.
2. Scope permission to the record owner, intended recipient, purpose, validity period and revocation state, evaluated per request.
3. Add protected encrypted storage, authentication-aware auditing, data minimization and deletion/retention policies.
4. Prove negative cross-account HTTP tests, consent revoke-then-replay and actual-device offline Windows QVAC tests.
5. Run synthetic human usability sessions with explicit participant consent; do **not** collect patient medical records.

## Decision
GO: isolated synthetic ownership/consent tests. HOLD: actual identity and HTTP integration. NO-GO: patient records, clinical and production deployment.
