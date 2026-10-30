# Build 20 — Submission Readiness Audit (private, synthetic only)

## Verified host reports
- Build 17 code gate: Windows PASS (user-supplied output).
- Build 18 offline host gate: HOST_OBSERVED_PASS (user-supplied output; not independently attested).
- Build 19 redacted evidence manifest: TECHNICAL_RECEIPTS=PASS (user-supplied output).
- QVAC receipt SHA-256: `771EB2353788CCE68C357939AC000E9F46EFB24DD6A0143974059EF2972EDB04`.
- HTTP E2E receipt SHA-256: `BF376766950DD34222E62466C9C72AAE3B7FDB86A4756D438BBA3D0CCB44360A`.

## Build 20 audit
Run in the Build 17 review worktree after fetching the latest draft PR branch, with the original project's ignored `local-evidence` directory:

```powershell
$e = "$env:USERPROFILE\Downloads\AI_Missy_Offline_FinalShip\local-evidence"
py .\scripts\build20_submission_audit.py `
  --manifest "$e\BUILD19_REDACTED_MANIFEST.json" `
  --evidence-dir $e `
  --output "$e\BUILD20_SUBMISSION_READINESS.json" `
  --bundle "$e\BUILD20_JUDGE_REVIEW.zip"
```

This script rehashes both original JSON receipts and verifies that they match the specific baseline fingerprints, checks that all Build 19 semantic gates are true, and writes a redacted ZIP with only a generated JSON report and review README. It **never** uploads raw receipts, transcripts, videos, model weights or private data, and does not use network access.

Optional: pass `--video "C:\path\to\uncut-demo.mp4"` to hash the video locally. Video presence/hash does not establish continuity, offline status or independent review.

## Outstanding blocking gates
- Uncut continuous video showing adapter disconnection and the complete offline model and HTTP/SQLite demonstration: **NOT VERIFIED**.
- `@qvac/sdk@0.22.0` license and redistribution review: **PENDING**.
- `LLAMA_3_2_1B_INST_Q4_0` model license, notices, model distribution policy: **PENDING**.
- Direct/transitive dependency notices: **PENDING**.
- DoraHacks event rules, eligibility, timeline and prior-work disclosure: **PENDING**.
- Privacy/clinical claims review: **PENDING**.
- Explicit public release and submission authorization: **NOT GRANTED**.

**Release and submission decision: NO_GO.** Technical evidence may be presented for review, not as independently certified offline proof.
