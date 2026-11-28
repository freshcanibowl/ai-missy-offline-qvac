# Build 33 — Cross-System Contract Validation (isolated synthetic simulation)

## Evidence boundary and provenance
Implemented in the existing AI Missy development branch. Reviewed Build30–32 source in the same repository. The interfaces below are **our proposed synthetic contracts**, not recovered or verified official ACE/PAIR API specs.

- **AI Missy adapter**: `ContractRequest` schema `missy-ace-pair-synthetic.v1`, synthetic-only case, subject, recipient, executor, event, purpose, event time and idempotency key.
- **ACE-like check**: reuses Build30's `SyntheticAceContract.permit` for subject/grantee/purpose/time/scope on each request, including retries.
- **Build32 segregation**: request must target a separately reviewed `APPROVED` case and must not spoof event or actor scope.
- **PAIR-like fixture**: records *only* a simulated in-memory acknowledgement bound to case, receipt, evidence hash, and recipient; no actual data delivery, FHIR API or contact with a hospital.
- **Idempotency**: one successful receipt per case and matching request; retries return the same reference. A temporary PAIR fixture outage returns `PENDING/PAIR_UNAVAILABLE`, with the receipt reference but no success acknowledgement; resumed retries reauthorize and verify evidence before final acknowledgement. Different idempotency keys or changed identity/event fields are rejected.
- **Evidence**: Build31 SHA-256 version and chain tip must remain current, including after approval. No clinical values, diagnoses or longitudinal outcome data are transferred.

## Fail-closed states
`BAD_CONTRACT`, `NOT_AUTHORIZED`, `CONFLICT`, `STATE_DENIED`, `INTEGRITY_FAILURE`, `UNKNOWN_CASE`, `REPLAY_BLOCKED`. A pending outage uses `PAIR_UNAVAILABLE`. These are **local Python return codes, not real HTTP error mappings**. There is deliberately no `/api/handoff` route.

## Tests
`tests/test_build33_cross_system_contract.py` contains 25 scenarios:
successful acknowledgement, same-key idempotent replay, outage and recovery, key reuse conflict, schema/identity/event/scope negative cases, revoked consent before and after receipt, stale/retracted evidence, cancelled/rejected case, audit outcome and unchanged server route boundaries.

Commands:
```bash
python -m unittest tests.test_build33_cross_system_contract -v
python -m unittest discover -s tests -v
```
Check GitHub Actions receipts for actual outcome, not just source presence. Chromium regression tests only the existing synthetic My Care UI, not actual three-system integrations.

## Red-team caveats
1. This is all within one Python process with dictionaries and synthetic role identities. It is **not networked integration** across AI Missy, ACE, and PAIR. No real-world identity verification, institutional consent, clinical validation, delivery evidence or PDPA legal determination.
2. The simulator's replay checks prevent *future* disclosure through this adapter after revocation; they cannot erase content previously viewed/copied.
3. The retry path is not durable against process restart. There is no transactionally committed outbox or independent acknowledgement signature. Production would need persistent idempotency store, verified API schema, deduplicated messaging, a real authority, case-level data ownership, end-to-end tracing and independent replay threat review.
4. SHA-256 matching inside the same process is not independent evidence anchoring.
5. No modifications to `server.py`, PAIR, ACE production or main branch.

## Gate
**GO:** isolated synthetic contract validation, negative testing and integration contract proposal.
**HOLD:** authenticated ACE/PAIR API discovery and provider-approved conformance tests, durable delivery, user/clinical review and institution onboarding.
**NO-GO:** using real patient health data or claiming a completed three-system clinical handoff.

| Why Continue | Stop / Kill Criteria |
| --- | --- |
| Able to exercise bounded request, authorization, receipt and ack | Different request replays same idempotency result |
| Explicit pending state and safe retry for outages | Outage recorded as real delivery |
| Revocation and evidence changes reject future replays | Stale evidence or revoked token grants access |
| Underlying clinical routes stay 403 | Synthetic adapter exposed as patient data API |
