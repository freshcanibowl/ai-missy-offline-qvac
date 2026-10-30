# AI Yako DoraHacks — Submission Draft (NOT SUBMITTED)

**Build title:** AI Missy Offline — Care Doesn't Disconnect

**Tagline:** A privacy-conscious, offline renal-care logging prototype powered by QVAC local AI, with human-confirmed records.

**Track:** Offline AI apps

**Team:** Confirm actual participating members; maximum 3. Remote participation allowed.

## Short description (paste into summary)

AI Missy Offline helps people managing kidney-care routines capture simple fluid-intake notes without relying on cloud AI. Running on a Windows device with QVAC, it interprets a short text note locally, proposes a structured intake record, and requires explicit human confirmation before storing it in SQLite. The prototype demonstrates a synthetic, offline-first workflow with replay protection and abstention when food data is insufficient. It is not a medical device or a substitute for clinical guidance.

## Full project description (paste into description)

### The problem
People managing kidney-care routines may need to log fluid intake consistently, including when connectivity is unreliable. Cloud-dependent assistants can interrupt the workflow or require sensitive text to be sent off-device. An AI-generated suggestion should never silently become a medical record.

### Our solution
AI Missy Offline is a Windows localhost prototype that uses QVAC for on-device interpretation of a fluid-intake note. The application converts an explicit text instruction such as **"Log 200 ml water"** into a proposed structured record, displays it for human confirmation, and then writes the confirmed record into a local SQLite database. Deterministic validation guards the record-writing step; a replayed confirmation is rejected. If the user requests a food-related conclusion without enough evidence, the app abstains rather than inventing nutrition values.

### Offline demonstration
The QVAC SDK and model are installed and downloaded while online, before the offline test. With network adapters disconnected, the Windows host ran local QVAC smoke and parse checks, a real localhost HTTP end-to-end workflow, SQLite confirmation, replay rejection and insufficient-data abstention. The host-reported result was `HOST_OBSERVED_PASS` on 30 Oct 2026 at approximately 23:00 MYT. A separate redacted evidence audit verified the SHA-256 of the two local receipts. This is host-observed evidence, **not** an independently reviewed uncut offline video; the required video remains outstanding.

### QVAC implementation
- QVAC SDK: `@qvac/sdk@0.22.0`
- Local model identifier: `LLAMA_3_2_1B_INST_Q4_0`
- Runtime: Windows, Node.js/QVAC, Python localhost HTTP server, SQLite and browser UI
- Relevant code: `scripts/preload-model.mjs`, `scripts/offline-smoke.mjs`, `scripts/qvac-parse.mjs`, `scripts/windows-offline-gate.ps1`, `scripts/live_http_e2e.py`
- Install and model preload: `npm install`, then `npm run model:preload` while connected to the internet
- Offline checks: `node scripts/offline-smoke.mjs` and `node scripts/qvac-parse.mjs --stdin` after disconnecting network adapters
- Evidence: Build 18 host run; Build 19 integrity PASS; Build 20 redacted review ZIP PASS
- Synthetic demonstration: daily recorded fluid total changes from **700 mL to 900 mL** only after confirmation

### Why this is different
Rather than presenting a free-form chatbot as a clinician, AI Missy keeps local language interpretation separate from record authorization. A deterministic validation and explicit user confirmation step control persistence. The result is a small, inspectable offline workflow, not a claim of clinical prediction or automated treatment advice.

### What needs internet
Initial package installation and model download; publishing source and video; any future hospital synchronization (not implemented). Core local text interpretation and local recording are intended to work offline after provisioning.

### Limitations and safety
Synthetic data only. No clinical validation or clinician-approved care plan, no medication or treatment recommendation, no fluid-overload prediction, no STT/TTS, no OCR, no clinical nutrition database, no mobile background notifications and no hospital/cloud sync. Browser-tab reminders are limited to an active browser session. No real patient data is used in the demo.

### Prior work and credits
The kidney-care use case builds on earlier PAIR and ACE Health OS concepts; CARLi, EvidenceKit and CAIOS informed generic safety and evidence design patterns. This QVAC Windows demo was implemented as an independent prototype. Prior work and third-party dependencies are disclosed in `docs/PRIOR_WORK_DISCLOSURE.md` and `docs/THIRD_PARTY_LICENSE_REVIEW.md`. The QVAC SDK is identified as Apache-2.0; Llama 3.2 model terms and transitive notices require separate review. Model weights are not included in the repository.

## Links and organizer-required items

| Form item | Actual status / value |
|---|---|
| Code repository | https://github.com/freshcanibowl/ai-missy-offline-qvac — **PRIVATE; NOT ACCESSIBLE TO JUDGES UNLESS ACCESS IS GRANTED** |
| Review PR | https://github.com/freshcanibowl/ai-missy-offline-qvac/pull/1 — **PRIVATE; NOT A PUBLIC SOURCE LINK** |
| Demo video URL | **MISSING / NOT VERIFIED** — must be a real judge-accessible URL showing uncut offline demo |
| Technical evidence | `BUILD20_JUDGE_REVIEW.zip` exists **locally**; no public or judge-accessible URL is verified |
| Device OS / RAM / GPU | Windows host used; exact OS edition, RAM, GPU and model footprint **NOT INDEPENDENTLY VERIFIED**. Read local host manifest and fill accurately |
| Model license | Llama 3.2 Community License terms review **PENDING** |
| Third-party notices | **PENDING** |
| Organizer eligibility / actual team | **MUST BE CONFIRMED** |
| Submission receipt | **NOT SUBMITTED / NO RECEIPT** |

## Organizer rules and timing (official event page)
- Official page: https://dorahacks.io/hackathon/ai-yako/detail
- Track: Offline AI apps
- Repository and recorded offline demo **required** and must be judge-accessible.
- Remote participation allowed; team up to 3; prior work must be disclosed.
- Deadline **extended** to **2026-10-31 01:00 MYT (UTC+8)** / 2026-10-30 20:00 EAT.
- Do not submit unsupported links, backdate evidence, falsely assert clinical efficacy or claim `Submitted` without an actual organizer receipt.

## Final submission checklist
- [ ] Confirm team members, account and eligibility statements
- [ ] Provide judge-accessible repository link or organizer-approved private access
- [ ] Provide real uncut offline demo video link accessible to judges
- [ ] Fill exact host OS, memory and model hardware details from verified local manifest
- [ ] Review SDK, Llama weights, dependencies and prior-work disclosures
- [ ] Ensure no secrets, real patient data or model weights are exposed
- [ ] Check all required form fields and link permissions
- [ ] Only then submit; save DoraHacks Build URL, ID, status and actual timestamp

**Current decision: DRAFT READY FOR FORM ENTRY; FINAL SUBMISSION BLOCKED BY REQUIRED ACCESSIBLE LINKS AND REVIEW.**
