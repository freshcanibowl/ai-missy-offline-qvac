# Build 25 — Real HTTP Request Tests in an Isolated Synthetic Identity Sandbox

Date: 2026-11-09. Draft feature branch only.

## Engineering result
- `metabolic/http_sandbox.py` creates a loopback-only HTTP server with HMAC-signed synthetic tokens. Only the test harness can mint them; there is **no HTTP token issuance endpoint**.
- In-memory SQLite stores `ALICE`, `BOB` and `REVIEWER` sample markers only. No actual readings, names, health histories, medical targets, or personal data are processed.
- Every request checks a signed token and exact scope; writes reject bad origins and hostnames. Owner read routes scope to the authenticated token subject only; explicit consent/revocation precedes reviewer preview. Reviewer preview is always `NOT_SENT`, `permission_to_transfer=false`.
- 20 HTTP-focused regression cases use localhost TCP, testing missing/forged/expired tokens, scope mismatch, cross-user reads/writes, consent revocation and replay, fake hosts/origins, forbidden sample fields and non-existent mint endpoint.

## Honest architectural boundary
This is NOT a real OAuth/OIDC provider, NOT connected to a registered provider, and NOT a production identity system. HMAC keys are generated inside the test process, and the synthetic test authority deliberately signs fake identities. It cannot prove real-world identity. Do not reuse the token minting authority in a production API or expose it to untrusted callers.

The standalone sandbox is not integrated into the existing `server.py`: the regular `/api/metabolic/*` routes **remain denied** as in Build 17. Existing QVAC water logging remains unchanged; no real medical data path is opened. This synthetic HTTP test suite does not prove Windows offline QVAC functionality or patient privacy compliance.

## Stop / kill criteria
- Any cross-account read/write or preview after revocation succeeds.
- Any endpoint issues credentials via HTTP, or any unsigned token is accepted.
- The existing `/api/metabolic/*` restriction is removed without a trustworthy production identity and consent system.
- CI fails or existing water logging regresses.
- Any sample or real patient information appears in audit logs or responses to the wrong user.

## Gates
GO: local isolated signed-token HTTP sandbox tests, if CI green.
HOLD: IDP sandbox with externally issued tokens, real clinical data access, production consent/patient relationship backend, encryption, independently reviewed auditing, real usability study and Windows offline evidence.
NO-GO: patient data, automated medical actions, PAIR transfer or any deployment for clinical use.
