# Build 34 — Independent Interface Discovery & Contract Conformance

**Date:** 2026-11-27. **Decision:** CONFORMANCE NO-GO. All findings below derive from directly fetched GitHub files; references are identified by their blob SHA in `evidence/build34_contract_conformance.json`. This is **not** a live production probe or an exhaustive inventory.

## Inspected repositories
- [ACE](https://github.com/freshcanibowl/ACE): its [README](https://github.com/freshcanibowl/ACE/blob/main/README.md) describes a monorepo and central shared contracts. A directly read implementation exists in [packages/contracts-schema/src/index.js](https://github.com/freshcanibowl/ACE/blob/main/packages/contracts-schema/src/index.js). It openly labels the wire format **DRAFT**.
- [PAIR](https://github.com/freshcanibowl/pair-renal-care): directly read [web/intake.js](https://github.com/freshcanibowl/pair-renal-care/blob/main/web/intake.js), [web/engine.js](https://github.com/freshcanibowl/pair-renal-care/blob/main/web/engine.js), [web/missy.js](https://github.com/freshcanibowl/pair-renal-care/blob/main/web/missy.js), [api/tencent-explain.js](https://github.com/freshcanibowl/pair-renal-care/blob/main/api/tencent-explain.js), and [api/health.js](https://github.com/freshcanibowl/pair-renal-care/blob/main/api/health.js).
- [AI Missy](https://github.com/freshcanibowl/ai-missy-offline-qvac): Build 33 `metabolic/cross_system_contract.py` remains a *different, in-process synthetic simulation*.

## Evidence-backed contract differences
| Area | Inspected implementation | Integration implication |
| --- | --- | --- |
| ACE EdgeCapture | `ace.edge-capture/0.1` with kind, patientRef, capturedAt, payload and provenance | Draft constructor, not proof of a live authorized ingestion API |
| ACE EngineInput | `ace.engine-input/0.1` wraps capture and baseline | Mapping from Missy event records still needs a verified authorized adapter |
| PAIR intake | `pair.renal-intake.v1` with deidentified privacy, extraction role, confidence and measurement array | **MISMATCH** with synthetic Build 33 request; do not cast directly |
| Escalation enums | ACE: `no_action`, `monitor`, `prompt_medical_review`, `urgent_review`. PAIR: `review_context`, `prompt_medical_review`, `urgent_professional_assessment` | **MISMATCH**; require explicitly reviewed strongest-state-preserving mapping |
| PAIR AI Missy explanation | `pair.ai-missy-request.v1`; runtime `pair.ai-missy-runtime.v1`, deterministic escalation cannot be overwritten | Confirmed as source code; not the same as receiving a care handoff |
| ACE ConsentRecord | `ace.consent/0.1` with patientRef, grantee, scopes, grantedAt, revokedAt | Type constructor is not a service that verifies identity, relationship, validity and revocation at handoff time |
| PAIR API | `api/tencent-explain.js` accepts POST explanation, may return `simulated_fallback` | **Not** an authorized patient handoff or PAIR receipt endpoint |
| Build33 | `missy-ace-pair-synthetic.v1`, `SYN-PAIR-ACK-*` | No matching real receiver endpoint was established from inspected evidence |

### Discovery limits
Several guessed paths such as `packages/auth-consent/src/index.js`, `apps/web-portal/package.json` and generic `openapi.json` were not found in the source locations tried. **This does not prove an auth service does not exist somewhere else**, or in another branch, deployment or repository. Code search returned no matches for several terms; do not interpret indexing gaps as definitive absence. In this inspection, no authorized, live three-system consent/handoff conformance evidence was acquired.

## Minimum acceptance gates
See the machine-readable [conformance evidence](../evidence/build34_contract_conformance.json) for G1–G8 with evidence required:
1. G1 official PAIR receiving ACK wire contract
2. G2 ACE real authentication, authorization and consent decision contract
3. G3 escalation enum compatibility mapping
4. G4 PAIR intake data/provenance adapter conformance
5. G5 cross-system identity and ownership binding
6. G6 durable idempotency, retry and independent audit
7. G7 authorized three-service loopback trace
8. G8 clinical and privacy governance

## Recommended next actions
**Do not implement a guessed production adapter.** Obtain full current ACE route definitions and PAIR receiver API spec (and versions), then create separate adapters with strict version negotiation; map escalation states with a conservative medical review gate; test every mismatch, authorization revocation and replay negative case on synthetic examples. Freeze any interface requiring real patient identifiers until explicit approvals and policies are in place.

## Release decision
- **GO:** evidence-based interface discovery and offline conformance review.
- **HOLD:** genuine independent ACE and PAIR integration, patient data ownership, real authorization and operational sign-off.
- **NO-GO:** live data transfer or clinical patient deployment.
- **Why Continue:** actual source contracts have been located, reducing guesswork.
- **Stop/Kill:** any code presents a draft schema or local `SYN-PAIR-ACK` as a verified production contract.

No changes were made to the ACE or PAIR repositories, AI Missy production server or main branch.
