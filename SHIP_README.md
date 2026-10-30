# AI Missy Offline — Ship Candidate (2026-10-30)

**Status: code tests PASS; Windows QVAC offline proof PENDING; public repository PENDING; DoraHacks submission PENDING.**

This is an independently packaged copy of Build 08, with historical release receipts removed to prevent confusion with real host evidence. It is a synthetic demonstration, not medical advice.

## Run in Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\Downloads\AI_Missy_Offline_ShipCandidate"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_HERE_WINDOWS.ps1 -Phase Preflight
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_HERE_WINDOWS.ps1 -Phase PrepareOnline
```

After model preload succeeds, physically disconnect all internet paths and record an uncut video. Then:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_HERE_WINDOWS.ps1 -Phase VerifyOffline
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_HERE_WINDOWS.ps1 -Phase ShipAudit
```

**Stop on failure; do not substitute simulated inference.** Evidence in `local-evidence/` is ignored by Git and should be shared privately after review. Do not include personal health data.

## Honest demo scope

QVAC local language extraction for explicit mL water logging, confirmation-gated SQLite persistence, synthetic recording target, abstention on food advice without verified nutrients, and browser-tab reminders. No STT/TTS, OCR, validated nutrition guidance, medication dosing, clinical prediction, or mobile background reminders.

## Submission checklist

- [ ] Windows real offline QVAC model load + inference + HTTP-to-SQLite evidence
- [ ] Uncut video showing disconnection and working app
- [ ] Public repository created and readable by judges
- [ ] License check for QVAC and Meta Llama model
- [ ] Organizer confirmation on remote participation eligibility
- [ ] DoraHacks project submitted, with submission receipt

No remote GitHub repository or DoraHacks submission was created as part of this package.

## Final Windows and publication checks
See `docs/BUILD_SHIP_NOW.md`; run `scripts/triage_windows.ps1` and `py scripts/submission_preflight.py` before publishing.

## One-command Windows diagnostic bundle
Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN_SHIP_DIAGNOSTICS.ps1`. It writes `local-evidence/AI_MISSY_SHIP_SUPPORT.zip`, containing **only** a redacted allowlisted diagnostic report and test counts. Share that ZIP to troubleshoot the host. This is not offline inference proof. Do not share the entire `local-evidence` folder.
