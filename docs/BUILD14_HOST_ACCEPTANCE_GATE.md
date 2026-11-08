# Build14 — Host Integration Acceptance Gate

Status: **LOCAL SYNTHETIC FIXTURE PASS; ORIGINAL WINDOWS CHECKOUT PENDING** (2026-11-08).

## Concrete discovery
Build13 `apply_build13.py` counts `with closing(connect(DB)) as c:` using a substring. Because original service may have the same substring in both GET and POST, this can reject the expected server as `UNSUPPORTED_SERVER_VERSION`. Build14 uses an exact full-line match of the standalone POST statement, retaining fail-closed behavior on drift. The corrected patch is included in the **local Build14 ZIP only**; not committed as runtime code here.

## Evidence
- Build14 test runner **3/3 PASS**, executed on an independent fixture with both GET and POST uses of the substring.
- Runner launched a real loopback HTTP subprocess and exercised legacy status and session; token-protected synthetic journal write; rejected unauthenticated/non-synthetic input; disabled personal plan; readback; and PAIR `NOT_SENT` preview. These are **fixture-based synthetic acceptance tests**, NOT original GitHub application host verification.
- Build14 ZIP SHA256: `16dd43fe9c7252c2c7729ed9ba0900b612dee8e3ad43c5ab86e358f7495dccd9`.

## Blockers
- Windows original repo full Python regression before and after patch: PENDING.
- Live QVAC inference, legacy fluid logging and actual browser operation: PENDING.
- Build14 addon/runtime not committed into GitHub PR; PR remains draft. No production change.
- GET journal and preview endpoints have no user-bound authorization and must remain synthetic-only. No patient data or real clinical use.

## Decision
GO: disposable Windows clone host acceptance; HOLD: PR code merge; NO-GO: production and real patients.
