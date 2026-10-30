# Build 19 — Judge Evidence Package (private / synthetic only)

## Evidence obtained from Windows host (user-supplied)
- 2026-10-30 23:00 local run: `BUILD07_LOCAL_OFFLINE_GATE=HOST_OBSERVED_PASS`.
- Python tests: `Ran 74 tests ... OK` in that host transcript.
- Semantic receipt: `qvac-verified-20261030-230025.json`, SHA-256 `771EB2353788CCE68C357939AC000E9F46EFB24DD6A0143974059EF2972EDB04`.
- Real HTTP receipt: `qvac-http-e2e-20261030-230025.json`, SHA-256 `BF376766950DD34222E62466C9C72AAE3B7FDB86A4756D438BBA3D0CCB44360A`.
- These are user-reported host observations; the raw receipts and uninterrupted video have **not** been independently reviewed here.

## Reproducible local audit
Run from a checkout with `scripts/build19_evidence_package.py` using the **original** project's ignored `local-evidence` folder:

```powershell
$e = "$env:USERPROFILE\Downloads\AI_Missy_Offline_FinalShip\local-evidence"
py .\scripts\build19_evidence_package.py `
  --evidence-dir $e `
  --output "$e\BUILD19_REDACTED_MANIFEST.json" `
  --expected-qvac-sha256 771EB2353788CCE68C357939AC000E9F46EFB24DD6A0143974059EF2972EDB04 `
  --expected-e2e-sha256 BF376766950DD34222E62466C9C72AAE3B7FDB86A4756D438BBA3D0CCB44360A
```

The script selects the most recent **matching timestamp pair**. If a newer pair exists, a hash mismatch will correctly fail; archive or specify the intended evidence directory rather than overriding hashes. No network or GitHub write is performed.

Optional: add `--video "C:\path\to\uncut-recording.mp4"` to record its hash and byte count **without copying video into the manifest**. This does not verify that it is uncut or prove network isolation.

## Evidence gates
- `BUILD19_TECHNICAL_RECEIPTS=PASS` means matching hashes and required JSON semantics only.
- `BUILD19_VIDEO_REVIEW=PENDING` always remains pending until independent human review.
- `BUILD19_PUBLIC_RELEASE=NO_GO` remains no-go pending license terms, organizer eligibility, video review, privacy and final authorization.
- Do not commit `local-evidence`, raw transcript, model weights, personal health data or video to Git.
- The demo uses **synthetic** renal-care records and does not constitute medical advice.
