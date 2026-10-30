# DoraHacks submission draft (do not claim submitted)

## Title
AI Missy Offline — Care Doesn't Disconnect

## Track
Offline AI apps

## Elevator pitch
AI Missy Offline is a private, on-device prototype for people living with kidney disease. It helps users capture an explicit fluid record, review it before saving, and understand a locally calculated daily total—even when the internet is unavailable. QVAC powers local language interpretation; deterministic checks and human confirmation prevent the language model from silently modifying health records.

## The problem
Care does not stop when the clinic closes or connectivity disappears. People may need a simple, accessible way to record intake and check their clinician-approved care plan. Cloud-only assistants can be unavailable or unsuitable for sensitive records.

## What we built during the hackathon
An independent Windows localhost app using Python, SQLite, browser UI and QVAC SDK 0.22.0. It includes a strict volume extraction contract, replay-safe user confirmation, local record persistence, a food-data abstention demonstration, and a browser-tab reminder. It is a synthetic, non-clinical prototype.

## Meaningful QVAC integration
- SDK: `@qvac/sdk@0.22.0`
- Model: `LLAMA_3_2_1B_INST_Q4_0`
- Model download: `npm install && npm run model:preload` (online once)
- Local inference: `npm run model:offline`, `node scripts/qvac-parse.mjs --stdin` (after disconnect)
- Files: `scripts/preload-model.mjs`, `scripts/offline-smoke.mjs`, `scripts/qvac-parse.mjs`
- Evidence: Windows Build 18 host-observed offline gate PASS and Build 19 hash/semantic manifest PASS; independent continuous-video review remains PENDING. See docs/BUILD19_EVIDENCE_PACKAGE.md.

## What still requires internet
Initial SDK installation and model download, source publishing, optional clinical sync (not implemented).

## What is NOT implemented
Voice STT/TTS, OCR, clinical-grade nutrition database, clinician-approved patient plans, prediction of fluid overload, real medication advice, mobile background notifications, or cloud/hospital sync. This is not a medical device.

## Prior work and licenses
The idea builds on previously developed PAIR renal-care and ACE Health OS concepts and borrows generic architecture lessons from CARLi, EvidenceKit and CAIOS. See `docs/PRIOR_WORK_DISCLOSURE.md`. The demo code is independently implemented. Verify the QVAC SDK license and Meta Llama 3.2 model license before submission.

## Required submission placeholders — replace only with real evidence
- Public repository: [NOT RELEASED]; private repository verified.
- Continuous disconnected-network demo video: [NOT VERIFIED / REVIEW PENDING]
- Hardware OS / RAM / GPU / model cache size: [LOCAL HOST MANIFEST EXISTS; NOT INDEPENDENTLY REVIEWED]
- Model license verification: [PENDING]
- Organizer eligibility confirmation: [PENDING]
- DoraHacks submission receipt: [NOT SUBMITTED]
