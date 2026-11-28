# AI Missy Build 29 — Longitudinal Care Context Foundation

## Scope
Feature branch `feature/daily-metabolic-care-build09`, Draft PR #5. This build **does not** create a longitudinal patient medical record. It adds a static, synthetic, read-only event timeline to `/today`, driven by the Functions choices already introduced in Builds 26–28.

## Unified observation/event contract (synthetic only)
Each frozen fixture event must contain:
- `id`: synthetic event identifier starting `SYN-`
- `module`: `glucose | pressure | renal | lipids`
- `event`: nominal non-diagnostic action, e.g. check-in or follow-up
- `observedAt` and `recordedAt`: explicit ISO 8601 timezone-offset timestamps; observed must be at/before recorded
- `source`: `synthetic_patient_demo` or `synthetic_care_plan`
- `confirmation`: always `unverified`
- `evidenceId`: independent synthetic evidence ID starting `SYN-`
- `synthetic`: always `true`
- `scope`: always `demo_only`

The timeline contains **four deliberately fictional, undiagnosed, non-numeric events**, sorted by observed time (newest first). It filters by enabled module. The visible "Show provenance" inspector discloses source, recorded time, confirmation, evidence ID, and scope in EN/中文/BM.

No task check-in generates an event, because a checked UI sample is not sufficient proof of a medical observation or external acknowledgement. Reload resets enabled functions, while hardcoded synthetic timeline fixtures remain in code.

## Guarantees and limits
- No real blood glucose/BP/eGFR/LDL lab readings, risk scores, clinical thresholds, longitudinal outcome claims, model predictions, clinical care instructions, network fetch, browser storage, new API, or patient export.
- Server still denies all `/api/metabolic/*` requests at HTTP 403.
- No ACE consent or live PAIR interface. Client-only Functions visibility is not an authorization or consent control.
- A real longitudinal event store would need identity binding, observation ownership, source verification, consent purpose, record correction/versioning, access control, retention, and independent medical review.

## Acceptance
Run `python -m unittest discover -s tests -v` and `python -m unittest e2e.test_build27_browser -v` under the existing Ubuntu 24.04 GitHub Actions workflow. Build29 contributes nine static/contract tests and seven browser tests. Confirm corresponding CI run logs before claiming PASS.

## Red-team gates
GO — local synthetic educational timeline after tests.
HOLD — actual patient history, permanent settings, real consent, institution pilot and integrated care handoff.
NO-GO — automatic drug, insulin or fluid recommendations; sharing patient data; live clinical operation.

Do not merge to main or deploy to production based on test green alone.
