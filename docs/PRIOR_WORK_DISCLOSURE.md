# Prior work and independent implementation disclosure

| Prior asset | Source | Existing capability | Build 04 usage |
|---|---|---|---|
| PAIR Renal Care | `freshcanibowl/pair-renal-care` (private) | Deterministic renal routing, AI Missy explanation contract, audit trail | Conceptual safety and separation of inference/decision logic; no direct source copied |
| CARLi Home | `freshcanibowl/carli-home-nebius-2026` | SQLite receipts, approval, replay defense, localhost server | Independently implemented analogous generic patterns; **Nebius cloud inference not used** |
| EvidenceKit | `freshcanibowl/EvidenceKit` | NLI/abstention/provenance, experimental | Insufficient-data handling concept; no NLI model or clinical evidence validation copied |
| CAIOS | `corwinlim/caios-2.0` (private) | Event provenance and longitudinal context | Architecture inspiration only; no veterinary rules or private source copied |
| ACE Health OS | Local Build 04C.2 and later versions not inspected here | Unknown | No source imported |

All synthetic patient values and implementation code in this archive were developed for the independent Build 02–04 prototype. The independent prototype is now in the private GitHub repository `freshcanibowl/ai-missy-offline-qvac`. No public release or DoraHacks submission has been verified. Check third-party licenses and organizer prior-work rules before submission.
