# Build 17 — HTTP-level Metabolic Deny-All (2026-11-09)

## Scope and deployment
This change is on the **feature branch only**, within the existing draft PR #5. **Not merged, not deployed, no patient data.** It changes the actual repository `server.py` GET and POST handlers to reject every `/api/metabolic` and `/api/metabolic/*` request with HTTP 403 and `METABOLIC_AUTHORIZATION_UNAVAILABLE`.

This deliberately preserves the original synthetic water logging / QVAC routes. It does **not** integrate the Build 13/14 zip metabolic read/write features. The presence of `metabolic/privacy_gate.py` does not establish trusted authentication; Build 17 uses a hard-coded route denial.

## Test contract
New `tests/test_build17_metabolic_http_gate.py` tests the actual `server.Handler` over a loopback TCP server: denied GET entries; denied GET PAIR preview; denied POST records; fake header + session token bypass; legacy session/status/UI; unknown routes stay 404.

Run on an isolated clone:
```powershell
py -m unittest discover -s tests -p "test_build17_metabolic_http_gate.py" -v
py -m unittest discover -s tests -v
```
These are **instructions, not passing CI evidence**. At commit time, no independent Actions status or original Windows run receipt was obtained. Observe the actual exit codes before upgrading gates.

## Mandatory remaining controls before real records
- Real identity provider, authoritative subject-to-record binding, scope and expiry of consent, revocation and audit
- At-rest encryption, protected credentials, backup/retention/deletion and care-provider RBAC
- Cross-user and rollback/replay/authorization-race negative tests with a real backend
- Independent clinical content review, careful CKD exceptions and medically appropriate escalation governance
- Windows QVAC offline proof and full legacy water logging regression

## Decision
**GO** for branch-level fail-closed code addition and test authoring. **HOLD** for real Windows/CI verification and actual patient-authorized implementation. **NO-GO** for clinical or production use.
