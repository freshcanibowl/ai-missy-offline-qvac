# Build 27 — Real Chromium Functions E2E evidence

Scope: AI Missy `/today` synthetic Functions UI on `feature/daily-metabolic-care-build09`.

## Browser validation
A separate GitHub Actions workflow installs the test-only Playwright 1.56 Chromium browser, performs `node --check web/today.js`, and runs eight real-browser tests in `e2e/test_build27_browser.py`.
- Default selected modules: glucose + pressure; renal + lipids opt-in
- Add kidney/lipids; correct sample tasks displayed
- Disable a module: hide sample task, clear its temporary selection and undo history
- EN/中文/BM names, retaining choice while changing language
- Undo/reset, keyboard focus and large-text toggle
- Mobile viewport 375 px no horizontal overflow
- Reload drops all module selections; browser storage stays unused
- UI does not call patient API; direct `/api/metabolic/entries` returns 403

## Evidence boundary
These are automated Chromium tests using a synthetic local server on the CI runner, not Windows browser or actual older-adult human testing. Browser E2E success is separately evaluated from the original Python CI run. No patient data, clinical targets, permanent preferences, live IDP, FHIR sync, CGM integration or clinical AI is enabled.

## Release gate
GO: synthetic browser UI only after independent browser CI success.
HOLD: Windows physical-device verification, human usability, durable user preferences, PAIR/ACE integration.
NO-GO: patient records or clinical deployment.

Do not merge into main or connect live medical records solely due to a green UI test.
