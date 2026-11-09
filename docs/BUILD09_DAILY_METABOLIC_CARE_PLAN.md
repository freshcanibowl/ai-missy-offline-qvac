# Build 09 — AI Missy Daily Metabolic & Kidney Care
Status: DESIGN/ISOLATED MODULE VALIDATION; NO REAL-PATIENT USE; NOT MERGED; NO LIVE QVAC CERTIFICATION.

## Product boundary
AI Missy is a voluntary daily journaling and health-literacy companion, NOT a diagnostic, medication titration, personalized renal diet or clinical triage device. PAIR retains clinician workflow, confirmed renal evidence and separate access controls. Do not share SQLite or health records between repos.

## Priority order
1. A 30-second, opt-in daily journal: BP (systolic, diastolic, pulse and timestamp), glucose (unit and fasting/meal context), movement, sleep, habits; laboratory lipid results only when actually measured.
2. Provenance per record: source manual/device/laboratory/caregiver, time zone, explicit user confirmation, correction history and visible missing-data state. Never treat missing readings as normal.
3. Personalization requires clinician-approved care plan. No generated fluid, potassium, phosphorus, protein, medication, or exercise prescriptions for CKD or uncertain comorbidities.
4. Patient engagement: no shame, no compulsory daily lipid testing, achievable actions, weekly trend reflection without assuming causation or promising reductions.
5. PAIR handoff: summary/export as a proposed artifact with patient consent; human approval and institutional identity checks before any clinical data transfer. No live integration in Build 09.

## Measurable outcomes (hypotheses, NOT traction)
- Opt-in daily logging completion, time-to-log, 7/28-day retention.
- Correction rate and unit/context errors.
- User-perceived burden and ability to understand why a record matters.
- Clinician assessment of whether summaries are useful or create duplicate work.
- Alert false-positive/false-negative rate after safety validation.

## Safety and privacy gates
P0: reject non-synthetic or identifying data in engineering test module; reject NaN, implausible input, malformed/missing units, impossible BP relationships, timezone-free/future observations, replay, hidden treatment changes.
P0: no inference of individualized clinical targets from population guidelines; low-confidence AI extraction requires explicit confirmation; separate deterministic medical escalation design from language model.
P0: offline claim needs device-level disconnection evidence; test data should never be pushed to public GitHub.
P1: proper authentication, encryption, consent, retention and deletion, RBAC, audit and clinical review before any real data.
P1: bilingual/trilingual content proofread; accommodations for older adults.
P2: validated BP/glucose device integrations, lab import, clinician-approved individualized targets, usability pilot after permissions.

## Research and copyright boundaries
Refer to ADA 2026 behavior/lifestyle standards, KDIGO 2024 CKD, 2026 AHA dyslipidemia patient messages, and 2024 ESC BP guidance externally. Do not ingest or embed copyrighted guideline text as LLM training/RAG material without appropriate permission.

## Stop/Kill
- Daily tracking adds burden without demonstrated patient value.
- Renal comorbidities make generalized advice unsafe.
- Clinical alert pathways cannot be validated or responsibly operated.
- Deployed integration cannot establish identity, consent, privacy and accountability.

## Work package
The independent Build09 daily_care.py and test_daily_care.py source package was validated locally with 16/16 synthetic unittest cases on 2026-11-08. This document does NOT claim the module has been integrated into the GitHub application. Integration and host regression are pending.