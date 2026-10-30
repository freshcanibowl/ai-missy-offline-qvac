# Build 23 — Synthetic Care Timeline Foundation

**Status: CODE COMMITTED, HOST VALIDATION PENDING.**

## Goal
Give AI Missy a local read-only longitudinal view of *confirmed synthetic* fluid-intake records. Build 23 extends Build 22 and is not a production patient-memory service.

## Implemented
- `care_timeline.py`: deterministic, bounded SQLite read of confirmed records.
- `POST /api/timeline`: existing loopback Host/Origin checks and session token; JSON body may include only `limit` and `offset`.
- UI: **View care timeline**, **Load more**, accessible text-only entries.
- Output schema: `ai-missy.synthetic-timeline.v1`, explicit `synthetic=true`.
- Default page size 20; maximum page size 50, maximum offset 1,000.
- Records include UUID, amount (mL), confirmation timestamp, event type and `cryptographic_attestation=false`.
- Free-text source, reminder titles, patient identifiers and model weights are excluded.

## Run on Windows
```powershell
git fetch origin build23/synthetic-care-timeline
git worktree add --detach "$env:USERPROFILE\Downloads\AI_Missy_Build23_Review" origin/build23/synthetic-care-timeline
Set-Location "$env:USERPROFILE\Downloads\AI_Missy_Build23_Review"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build22-host-gate.ps1
py server.py
```
Open `http://127.0.0.1:8766`. Use an **isolated synthetic SQLite DB** to avoid mixing test records. After a confirmed 200 mL log, click **View care timeline** and verify the event is visible, then **Download synthetic JSON** to compare.

## Tests
- `tests/test_care_timeline.py`: empty timeline, restart persistence, paging, input bounds, no raw text leakage, malformed timestamp rejection.
- `tests/test_http.py`: token protection, invalid limits and unexpected field rejection.
- `py -m unittest discover -s tests -v`
- `node --check web/app.js`

## Explicit non-goals
- No real patient accounts, consent workflow, cross-device sync, encryption-at-rest, tamper-evident chain, medical advice, diagnosis, or treatment.
- The demo token is **not** production-grade authorization.
- `cryptographic_attestation=false` means the UI must not call this a cryptographically verified audit log.
- Offset pagination is deterministic only for a static dataset; concurrent insertions can shift pages.
- The `source_type` field denotes locally confirmed storage, **not independently verified QVAC provenance**.

## Next security gates before real data
Threat model; patient identity; purpose-bound consent and revocation; encrypted storage and key recovery; deletion/retention controls; role-based access; clinical review; audit design; privacy/legal/regulatory assessment.

## Release gate
No main merge, public deployment, or clinical use until Windows tests and UI verification pass and security review is complete. Keep the hackathon submission unchanged.
