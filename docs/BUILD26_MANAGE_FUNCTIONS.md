# Build 26 — AI Missy Manage Functions (Synthetic Preview)

## What works
The existing `/today` page now has a **Functions / 管理功能 / Urus Fungsi** section. Users can independently select Blood glucose, Blood pressure, Kidney care and Blood lipids. Only enabled modules show their example task; switching one off removes its sample selection and clears undo history. The general activity and food-habit examples remain available.

The page keeps English, Simplified Chinese and Malay, the larger-text option, keyboard focus restoration and undo/reset sample-task controls. A visible **SESSION ONLY** label explains that the module choices exist only while this page remains open.

## Important boundaries
No readings, risk scores, prescriptions, treatment targets, diagnoses, lab values, real patient records, network calls or persistent settings are added. Module management affects only the local *display*, not genuine record ownership, caregiver consent, scheduling or clinical monitoring. The server continues to hard-deny `/api/metabolic/*` GET and POST (HTTP 403).

The user has requested selectable function management, not production patient data capture. The project branch remains `feature/daily-metabolic-care-build09` and the draft PR is #5. No changes to main, PAIR or ACE production.

## Evidence
Run `python -m unittest discover -s tests -v` and Build17 hard-deny tests, verify GitHub Actions execution. The new Build26 contract checks static UI and source boundaries; it is **not** a real browser usability or accessibility study. Windows QVAC offline and live patient identity remain unverified.

## Subsequent implementation gate
After verifying the UI with real Windows/Android browsers using synthetic records, introduce true preference persistence only when there is a trustworthy per-user identity and privacy scope. Persisting a disease module selection can disclose health interests and should be treated as sensitive. Any backend extension needs purpose-limited consent, authorization and validated data provenance.

## GO / STOP
GO: optional synthetic care modules in development preview.
HOLD: durable per-user preferences, actual observation data, clinical carepath integration.
NO-GO: automatic medical advice, clinical deployment or patient data release.
