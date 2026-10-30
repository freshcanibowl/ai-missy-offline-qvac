# Build 17 — Release readiness and evidence gates

Repository: `freshcanibowl/ai-missy-offline-qvac` (PRIVATE); verified initial commit `ded565a846667d84c68705623c9888efdb7bfeb3`.

## Verified scope
- The 74 original Python tests pass in a local source snapshot; this does **not** prove live QVAC model inference.
- `node --check` validates JavaScript syntax only, not model execution.
- The private repository and its initial commit are independently verified. Public release and DoraHacks submission are **not performed**.
- Text input is implemented. STT/TTS, OCR, clinical prediction and validated nutrition advice are **not** implemented.

## Required gates before PUBLIC release
- [ ] Verify `@qvac/sdk@0.22.0` license and redistribution terms, with authoritative URL, reviewer and date.
- [ ] Separately verify `LLAMA_3_2_1B_INST_Q4_0` model license, attribution, acceptable use and weight redistribution restrictions.
- [ ] Review transitive dependency licenses and notices.
- [ ] Update stale README / ship status / judge instructions to reflect PRIVATE GitHub publication, not public availability.
- [ ] Reproduce actual Windows offline QVAC cold load, inference and real HTTP → SDK → SQLite persistence while network adapters are disconnected.
- [ ] Capture a single uncut video showing network disconnection, synthetic 200 mL log and confirmation, persistence after refresh, and food abstention.
- [ ] Review evidence for personal data, secrets and medical overclaims; retain sensitive host receipts outside Git.
- [ ] Record hardware, OS, runtime versions, exact model identity/checksum, and clean-machine setup.
- [ ] Verify organizer eligibility, prior-work rules and deadline directly.
- [ ] Obtain explicit authorization before public visibility, release, or DoraHacks submission.

## Baseline audit defect
The first commit intentionally excludes `scripts/publish-new-repo.ps1` from Git. However `scripts/final_release_audit.py` still requires it, producing a misleading failure. Correct that obsolete prerequisite in a reviewed change; **do not add an unsafe publication script just to satisfy the audit**.

**Decision: CODE TESTS PASS (snapshot); PUBLIC RELEASE NO-GO pending licenses, evidence, video and documentation.**
