# AI Missy × PAIR × ACE — Build 32: Authorized Handoff Workflow Simulation

## Implementation (synthetic only)

New `metabolic/handoff_workflow.py` provides a **test-only** in-memory state machine:
`PROPOSED → APPROVED → EXECUTED`; alternative terminal states: `REJECTED`, `CANCELLED`.

Roles are intentionally separate: **proposer**, **reviewer**, **executor**, and **recipient**. The reviewer cannot approve their own proposal; executor cannot be proposer, reviewer or recipient. A receipt is only issued through the Build31 `SyntheticHandoffService` after a separate review and successful re-validation of current Build30 revision/evidence hashes.

The recipient's subsequent read re-checks the Build30 synthetic ACE-like authorization contract, the receipt and ledger integrity. Revocation, expiry, correction, retraction and unrelated chain changes invalidate further access. Case rejection reason is selected from an allowlist; free-text clinical notes are not accepted. Proposer can cancel pending or approved cases but not executed cases.

## Auditing and limits

Each workflow attempt at sensitive transitions generates a bounded `AuditEntry` with sequential SHA-256 linkage, actor ID, event, outcome and reason. Negative paths such as bad role and denial are audited. Only a synthetic reviewer role can access the in-memory audit tuple. Hashing is **not** an independent trusted timestamp, secure ledger or digital signature; a party controlling the entire process could rewrite the chain.

The test fixture's `role_assignments` dictionary is **not a real identity provider**. Passing a synthetic actor ID is impersonable by a caller with object access. The Build30 test-only HMAC authorization is not real ACE approval; the Build31 receipt is not delivered to a hospital. No new server route exists; `/api/metabolic/*` remains denied (HTTP 403). No patient data, automated diagnosis, clinical decision, medication recommendation, API transport, persistence or public endpoint.

**Critical**: revocation prevents future reads in this process, not deletion of a previously displayed or copied preview. Handoff approval is workflow approval of fictional evidence, *not* clinical review. Approval does not change observation confirmation from `unverified`.

## Verification
```bash
python -m unittest tests.test_build32_handoff_workflow -v
python -m unittest discover -s tests -v
```
There are 30 Build32 automated cases: role checks, separation of duties, workflow ordering, refusal and replay, cancellation, revocation before/after execution, stale evidence, chain tampering and audit visibility. Verify GitHub CI logs before stating test PASS.

## Why Continue vs Stop / Kill
| Why Continue | Stop / Kill Criteria |
| --- | --- |
| Separate proposer, reviewer and executor | Same identity or unchecked role can approve and execute |
| Evidence-bound approval before execution | Changed version accepted without re-approval |
| Read checks authorization again | Revoked/expired grants read successfully |
| Denial audit for misuse investigation | Failed attempts are silently accepted or omitted |

**GO**: synthetic state machine and negative security tests after CI acceptance.
**HOLD**: actual ACE IAM, consent and audit contracts, actor authentication, durable database, institutional integration, Windows device and human operational validation.
**NO-GO**: real patient or clinic data, clinical deployment, unrestricted agent actions or background delivery.

Branch: `feature/daily-metabolic-care-build09`; Draft PR #5. Main branch unchanged.
