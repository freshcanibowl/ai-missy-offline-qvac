# AI Missy Build 28 — My Care Dashboard (synthetic preview)

**Scope:** Single /today page, no new patient APIs, on development branch `feature/daily-metabolic-care-build09`.

## Delivered
- My Care Dashboard displayed before Functions.
- Glucose, blood pressure, kidney and lipids cards appear only if enabled in Functions.
- Progress is the number of selected *example task checkboxes* for enabled clinical modules; it is not an adherence score, health measure or medical recommendation. General activity and food habit examples are intentionally excluded from clinical module counts.
- Each care card includes a View Task button that focuses the related synthetic checkbox.
- Instant synchronization on module toggle, task selection, undo and reset.
- All labels and status strings in English, Chinese and Malay, with an empty state for no enabled modules.
- Mobile responsive and large-text CSS styles; no localStorage, sessionStorage, IndexedDB, fetch, patient records or medical values.

## Evidence & red team
Build27 Chromium tests remain in `e2e/test_build27_browser.py` with seven Build28 scenarios added (15 total). The existing Python regression suite and explicit HTTP hard-deny remain unchanged. CI can pass on Ubuntu but does not replace Windows/Android physical browser and older-adult usability tests.

**GO:** synthetic workflow demonstration and optional module selection after browser CI pass.
**HOLD:** per-person settings persistence, real longitudinal observations, PAIR/ACE live integration and external clinical review.
**NO-GO:** real patient data collection, clinical decision-making, unsupervised medicine or fluid-limit instructions and production release.

No main branch merge or production deployment is authorized by this change.
