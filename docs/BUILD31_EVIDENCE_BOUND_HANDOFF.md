# Build 31 — Evidence-Bound Care Handoff (Synthetic Preview)

## Implemented code
- `metabolic/evidence_handoff.py`: a synthetic-only handoff service with SHA-256 bound opaque receipts and a read-only preview.
- `tests/test_build31_evidence_handoff.py`: automated positive, negative, integrity and authorization tests.
- Existing Build30 `SyntheticMemoryLedger` and `SyntheticAceContract` reused without modifying the production app.

## Workflow
1. The in-memory synthetic ledger records an **unverified** observation; revision chain integrity is checked.
2. A separately issued test-only grant authorizes `care_demo_review`, for one synthetic subject and one synthetic reviewer within explicit dates.
3. A handoff service is initialized with the **synthetic owner subject**, preventing an otherwise valid grant for a different subject from accessing this ledger.
4. `issue_receipt` returns a frozen receipt binding event ID, current version, version hash, global chain tip, subject, grantee, purpose and issue time. The receipt contains no observation content.
5. `inspect` rechecks ledger integrity, owner scope, synthetic consent, bound version, manifest hash and global chain tip before it returns an immutable `HandoffPreview`.
6. If the record is corrected or retracted, any part of the ledger is changed, or access is revoked/expired, the prior handoff receipt becomes unreadable. Issue a new receipt only with newly validated evidence and valid authorization.

## Critical boundaries
- **No delivery or transfer takes place.** This is an in-memory read-only preview, not an actual PAIR handoff, an ACE service integration, a notification, a clinical report, a new HTTP endpoint, or data exchange.
- No live identity, real subject, patient record, clinical thresholds, prescriptions, care decisions, FHIR exchange, persistence or export. `server.py` and `/api/metabolic/*` remain unchanged and hard-denied.
- No trust should be placed in the test-only HMAC fixture as a genuine ACE signature or consent proof.
- **Revocation prevents future authorized reads in this process, not retroactive erasure of previously displayed or copied data.**
- SHA-256 only detects mutation relative to trusted hashes; it is not an independent signature, durable anchor or prevention of full-chain rehashing.
- No independent patient ownership service exists; the owner binding is an explicit test fixture scope, not verified real-world identity.
- Receipts stored in RAM; process restart loses them. A production design needs retention policy, durable audit, key management, evidence ingestion and credential verification.

## GO / STOP
GO: synthetic-only evidence chain → independently authorized receipt → rechecked preview.
HOLD: production identity, real consent, PAIR/ACE interface contract, human review, Windows/device validation, patient data governance.
NO-GO: real patient exports, clinical decision support or patient-facing deployment.

Execute `python -m unittest discover -s tests -v` and review GitHub Actions logs; separate Chromium browser regression must also remain green. **Do not merge to main solely on these tests.**
