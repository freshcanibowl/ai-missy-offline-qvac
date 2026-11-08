# Build16 Privacy Gate (2026-11-08)
Security-first **DENY-ALL** policy prototype in `metabolic/privacy_gate.py` and tests.
No patient identity/consent backend has been integrated; all data reads and exports are rejected regardless of caller-supplied flags. This is deliberate: a loopback session token is NOT patient authentication.
- Isolated local source was tested: 13/13 unittest PASS.
- Code is now in the existing draft feature branch only. New tests in GitHub must still be run by CI, and the policy is **NOT wired into existing server.py**.
- The current Build13/14 ZIP still contains an insecure synthetic-only read path. It has **not** been converted into a real clinical product.
- DO NOT route actual health data to the current `/api/metabolic/entries` or `/api/metabolic/pair-preview` endpoints.
- To integrate safely, first establish trusted user identity, patient-to-record binding, scoped consent, audit, storage encryption and negative cross-user HTTP tests. Existing water/QVAC APIs must keep regression tests.
Release: synthetic policy tests GO; actual HTTP authorization and QVAC host validation HOLD; production and clinical NO-GO.
