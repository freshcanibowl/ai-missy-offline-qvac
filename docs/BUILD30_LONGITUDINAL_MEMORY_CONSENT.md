# Build 30 — Longitudinal Memory Integrity & ACE Consent Contract (Synthetic)

## Implementation status
Implemented directly on `feature/daily-metabolic-care-build09`, alongside Build 29's static synthetic timeline. No merge to main and no production deployment.

### Source files
- `metabolic/longitudinal_memory.py`: frozen synthetic observations, SHA-256 content binding, global chronological hash chain, per-observation revision link, optimistic version checking, append-only `create / correct / retract` tombstones, chain verification **before reads and writes**.
- `metabolic/consent_contract.py`: default-deny external authorization adapter. An explicitly named **SyntheticAceContract** simulates a separate approval authority for **tests only**, using HMAC-signed synthetic fixture grants, purpose/scope/subject/grantee/validity checks, replay rejection and immediate revocation.
- `tests/test_build30_memory_consent.py`: 24 executable tests with negative scenarios.

### Observation contract
`Observation(event_id,module,event,observed_at,recorded_at,source,evidence_id,confirmation="unverified",scope="demo_only",synthetic=True)`.
- IDs are `SYN-*` and never real patient identifiers.
- Only `glucose | pressure | renal | lipids` and known non-clinical event kinds.
- Only controlled synthetic fixture sources, explicit UTC+08:00 timestamp offset, observed <= recorded.
- No numeric blood sugar, blood pressure, eGFR, lipid results or medical interpretations. Event correction is a new version, never an overwrite.

### Revision contract
- A revision binds action, immutable observation, position, version, previous global hash and previous per-event hash into its SHA-256 digest.
- Duplicate creation, stale version, cross-module reassignment, edits after retraction, broken links and modified content fail verification.
- `retract` is a tombstone, leaving earlier versions available for *authorized synthetic audit access*; it is not deletion of personal data.
- The in-memory store has **no persistent backend, external anchoring or durable audit record**. A party able to rewrite and rehash the entire in-memory chain could fabricate a new consistent chain. SHA-256 alone is tamper-*evident under a trusted comparison*, not a full tamper-proof or nonrepudiation system.

### Consent contract
- Missing adapter = deny all; all read paths check authorization.
- Mock fixture grants must match synthetic subject, grantee, purpose, `timeline:read` scope and validity interval, and pass HMAC signature comparison.
- Revoking the synthetic grant immediately blocks subsequent reads. A *new independent synthetic grant* may permit future authorized reads; a revoked grant cannot be resurrected.
- The HMAC testing key is NOT an ACE signing credential, verified identity, patient consent, legal authorization or clinical approval.
- Do not call `issue_fixture` from a production API; do not substitute frontend function toggles for permission checks.
- This implementation does not establish purpose-bounded consent for actual users, nor test consent from a real identity provider.

### Verification
Full repo test command:
```bash
python -m unittest discover -s tests -v
```
Focused:
```bash
python -m unittest tests.test_build30_memory_consent -v
```
Existing browser UI regression:
```bash
python -m unittest e2e.test_build27_browser -v
```
The new ledger is intentionally **not** exposed through `server.py` or the `/today` UI. Existing `/api/metabolic/*` HTTP routes remain hard-denied 403. Build 29's four timeline fixtures remain read-only in the UI. Bridging the ledger to real UI/API requires separate authorization and data governance review.

## Why Continue / Stop-Kill
| Why Continue | Stop / Kill Criteria |
| --- | --- |
| Immutable synthetic event versions and visible provenance | Event tampering, rollback or stale version accepted |
| Reads fail closed without a separate grant | Access after revocation, cross-subject or expired grant succeeds |
| Traceable correction and retraction semantics | A prior version disappears silently |
| No patient records or production integration | Any route accidentally starts accepting real metabolic writes |

## Gate
- **GO**: synthetic-only memory and consent-contract engineering tests.
- **HOLD**: real identity provider, ACE signed approval schema, production database, legal consent mapping, true patient longitudinal memory, Windows/device acceptance, real clinicians.
- **NO-GO**: patient/clinic data use, autonomous clinical decision support, insulin or medicines management, patient-facing clinical deployment.

Testing these contracts does not validate HIPAA/PDPA/MDA compliance or the effectiveness of any medical intervention.
