# Build 21: Synthetic Usability Walkthrough — Evidence Boundary
Date: 2026-11-09

## Implemented on development branch
- A three-step, three-language task rehearsal on `/today`: select a sample item, undo the selection, reset.
- Undo history is page-memory only; reset clears it. No medical readings, persistence, analytics, networking, or real patients are involved in this preview.
- `/api/metabolic/*` stays blocked (403). Main and PAIR production were not touched.
- Nine new automated contract tests cover walkthrough, undo, reset, keyboard focus, language, no persistence and source safety.

## Evidence quality and separate gate
GitHub CI verifies static code contracts and basic HTTP behavior; it does **not** verify whether an older adult actually understands the UI, whether screen readers announce everything correctly, or whether Windows QVAC operates offline.

### Proposed observational usability protocol (NOT conducted)
- Recruit consenting adults who can evaluate the **synthetic** UI, including some who have limited digital confidence. Do not collect medical history or measurements.
- Counterbalance EN/ZH/BM where relevant; use an independent observer and explicit permission for any notes.
- Task A: open /today and explain the synthetic/no-storage label; B: choose one sample item; C: undo; D: increase text; E: change language; F: reset; G: explain whether data was saved and whether an AI medical target was generated.
- Log task completion (yes/no), number of prompts, errors, perceived difficulty and qualitative feedback without personal identifiers.
- Initial *proposed* gate: 5 or more evaluators; 100% should understand the no-data-storage and no-medical-advice boundary, and >=80% should independently complete B/C/F. This is a suggested product threshold, **not observed evidence or statistical proof**.
- Stop/kill: any participant believes a clinical reading was recorded, any task requires someone to disclose health information, or any test indicates inaccessible keyboard/reader behavior. Fix and retest.

## GO/HOLD
GO: branch-level synthetic UI iteration and CI. HOLD: real usability evidence and full Windows QVAC test. NO-GO: clinical or production usage.
