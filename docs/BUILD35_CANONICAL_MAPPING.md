# Build 35 — Canonical Contract Mapping & Negative Conformance

**Status: SYNTHETIC ENGINEERING ONLY. Source inspection does not prove wire conformance, actual consent or clinical safety.**

## Verified upstream source (GitHub blob SHA, inspected 2026-11-28)
- ACE `freshcanibowl/ACE:packages/contracts-schema/src/index.js` @ `d582ecdce22f3c85d0023a41574535fc079ce31d`: draft `ace.edge-capture/0.1`, `ace.engine-input/0.1`, `ace.escalation-event/0.1`, `ace.consent/0.1`. ACE consent constructor does not prove authoritative identity/permission checks.
- PAIR `freshcanibowl/pair-renal-care:web/intake.js` @ `f57c2d9fa7fa56bf5524d08840e73ee939859716`: `pair.renal-intake.v1`, deidentified privacy, extraction agent-only and measurement confidence checks. `confirmationReasons` detects issues but does not itself establish actual human confirmation.
- PAIR `web/engine.js` @ `6d51676aca588df9b6166405b3f93002ea24c057`: deterministic renal demo rules and `urgent_professional_assessment`.
- PAIR `web/missy.js` @ `0fe60c5a6e591fd39924b18f3c149b605967e546`: `pair.ai-missy-request.v1`, preserves escalation state in `validateMissyResponse`.
- AI Missy Build30 `metabolic/longitudinal_memory.py`: source-backed, **unverified but no numeric lab value** demo task events. They **cannot** be promoted to a PAIR measurement.

## Implemented synthetic-only adapter
`metabolic/canonical_mapping.py`: two *proposed* mappings for offline analysis.

1. **Conservative escalation mapping, pending clinical sign-off**
    - PAIR `review_context` → ACE `monitor` (NOT `no_action`)
    - PAIR `prompt_medical_review` → ACE `prompt_medical_review`
    - PAIR `urgent_professional_assessment` → ACE `urgent_review`
    - Unknown levels, missing deterministic engine authority, an ACE output inconsistent with policy, or an AI Missy response that changes PAIR's state fail closed.
2. **Synthetic lab extraction fixture → PAIR proposed intake preview**
    - Requires `missy.synthetic-extraction.v1`, `SYN-*` subject ownership binding, `authorization_verified=True` provided by the synthetic harness, and explicit human confirmation with synthetic actor ID.
    - Requires `deidentified=True`, no retained identifiers, `extract_and_normalize_only`, and `clinical_inference_performed=False`.
    - Requires explicit `+08:00` capture date, unique allowlisted measurement codes, finite positive values, declared units, per-measurement evidence references, confidence >=0.95 (local conservative policy), and creatinine.
    - Returns a `pair.renal-intake.v1`-shaped **in-memory, synthetic** fixture with an additional `assurance.release_gate=NO_GO` field. This additional field has **not** been accepted or negotiated by PAIR.
    - Real labs, patient names, missing consent, unknown units, low-confidence extraction and raw Build30 task observations are blocked.

## Explicit limitations
- This module does not import or execute the upstream ACE and PAIR JavaScript source in the same CI run; no independent cross-repo data-contract conformance has yet occurred.
- Synthetic authorization boolean and confirming synthetic actor ID do not prove a real patient has consented or any clinician validated medical findings.
- The chosen escalation mapping is proposed conservative behavior, **not clinically validated equivalence**. In particular, the ACE and PAIR labels are distinct source terminology.
- PAIR `web/intake.js` allows some cases that our preview intentionally blocks (e.g. low confidence), but its permissiveness does not establish clinical safety. PAIR also requires real confirmation workflow outside its basic validator.
- No HTTP endpoint, persistence, clinical prediction, prescriptions, actual ACE/PAIR permissions, real dataset, or live data transfer introduced.
- Source code SHA and tests are engineering evidence, not production integration approval.

## Testing
```bash
python -m unittest tests.test_build35_canonical_mapping -v
python -m unittest discover -s tests -v
```
Build 35 adds 35 fixture, mapping and negative security tests. Existing Chromium tests are UI regression only. Review actual GitHub Actions logs before claiming PASS.

## Next gates
| Gate | Status | Evidence needed |
| --- | --- | --- |
| Synthetic mapping with negative tests | GO only if CI PASS | full test run |
| ACE/PAIR shared schema version negotiation | HOLD | actual upstream author approval, no silent type casting |
| Pair source JS executed against mapped fixtures | HOLD | independent JS fixture suite, version-pinned imports |
| Real identity, consent, human verification | NO-GO for clinical use | independent authoritative service, legal requirements |
| Networked three-system delivery and ACK | HOLD | real endpoints, secure retry, independent signatures |

**Why Continue:** Source differences are now explicit and unsafe shortcuts are rejected in code.
**Stop / Kill:** Any unverified observation becomes a lab result, clinical escalation is lowered, or synthetic approval is presented as live consent.
