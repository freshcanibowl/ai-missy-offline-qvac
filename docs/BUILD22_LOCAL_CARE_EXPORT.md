# Build 22 — Local Care Record Export (synthetic-only)

## Scope
This increment is a **local data portability prototype** for AI Missy, not a medical record or clinical integration. It preserves the AI Yako submission branch and does not modify production infrastructure.

## User flow
1. Run `py server.py` on Windows after the existing setup.
2. Visit `http://127.0.0.1:8766`.
3. Use QVAC to propose a fluid note, explicitly confirm the record, and refresh.
4. Click **Download synthetic JSON** under **Export local care record**.
5. Inspect `ai-missy-synthetic-care.json` locally. No network request or external storage is needed.

## Contract
- `POST /api/export` requires the existing loopback Host/Origin checks and `X-Missy-Token`.
- Request body must be an empty JSON object.
- `schema_version=ai-missy.synthetic-care.v1`, `synthetic=true`, `generated_at` UTC.
- Export contains plan ID, synthetic baseline, confirmed event IDs/volumes/timestamps, and total.
- Free-text notes, reminder titles, model weights and patient identifiers are deliberately **not exported**.
- Limit of 1,000 confirmed events; larger exports fail closed with `EXPORT_TOO_LARGE`.
- No new third-party dependencies or cloud APIs.

## Reproduction and tests
```powershell
py -m unittest tests.test_care_export tests.test_http -v
py -m unittest discover -s tests -v
py server.py
```
Run the local UI, create a confirmed 200 mL event and download JSON. Verify `recorded_total_ml=900` on a fresh synthetic database. If a previous SQLite file contains additional confirmed records, totals will differ; use a **new temporary synthetic DB** for a clean test.

## Limitations / release gates
- Existing localhost token is a demo protection, **not production authentication**.
- Exported JSON is not encrypted or signed; users must store it securely.
- No consent ledger, encryption-at-rest, deletion lifecycle, user accounts, identity binding, clinical FHIR mapping, or real-patient support.
- No claim of real patient privacy compliance or medical-grade security.
- Run the tests and record actual Windows host results before calling this Build 22 PASS.
- Do not merge into `main` or deploy without review and approval.
