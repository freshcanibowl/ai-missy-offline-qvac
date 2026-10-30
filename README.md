# AI Missy Offline — Build 08 | Ship-readiness hardening

**Status: CODE GATE only; REAL WINDOWS QVAC OFFLINE UNVERIFIED; NO GITHUB PUBLICATION; NO DORAHACKS SUBMISSION.**

A synthetic-only, local Windows browser demonstration. It is not a medical device and does not provide medical or nutrition treatment recommendations.

## What's new in Build 08

- Prevent ambiguous historical, future, hypothetical, spilled or questioned fluid amounts from being silently recorded as today's intake. An explicit recording or consumption statement is required.
- Added 10 safety regression tests, Build 08 release audit, and a single Windows command entrypoint.
- UI now calls the 1,000 mL synthetic limit a **recording target**, not a medical allowance.
- Retained the actual QVAC SDK integration (`@qvac/sdk@0.22.0`) and real HTTP → QVAC → SQLite E2E; no cloud fallback.
- Source ZIP does not contain QVAC model weights, Node modules, real patient data or offline evidence.

## Windows runbook

Unzip to `%USERPROFILE%\Downloads\AI_Missy_Offline_Build08`, then in PowerShell:

```powershell
Set-Location "$env:USERPROFILE\Downloads\AI_Missy_Offline_Build08"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build08.ps1 -Phase Preflight
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build08.ps1 -Phase PrepareOnline
```

**After successful preload, disconnect Wi-Fi, Ethernet, VPN and hotspots; record an uncut video.**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build08.ps1 -Phase VerifyOffline
py server.py
```

Browse to http://127.0.0.1:8766 and test `Log 200 ml water` → confirm → 900 mL after refresh, banana abstention, and a two-minute browser-tab reminder. In a second terminal after the demo:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build08.ps1 -Phase ShipAudit
```

**If preload or inference fails, stop.** Share error output, do not fabricate a QVAC receipt.

## Important limitations

QVAC only extracts explicit fluid logging intent, not clinical advice. No STT/TTS, OCR, validated renal food database, prediction, real patient identity, encryption or hospital integration. Reminders only work while the browser tab remains open. All patient values are synthetic; the 1,000 mL target is not a prescription.

Official references: https://docs.qvac.tether.io/sdk/system-requirements/ and https://docs.qvac.tether.io/sdk/ai-capabilities/text-generation/ .

## Shipping

See `docs/BUILD08_SHIP_CHECKLIST.md`, `docs/DORAHACKS_SUBMISSION_DRAFT.md`, `docs/PRIOR_WORK_DISCLOSURE.md`. Public GitHub publishing is not performed by this ZIP. `scripts/publish-new-repo.ps1` defaults to dry-run and requires explicit confirmations for publication. Do not publish `.env`, `local-evidence`, model weights, logs, SQLite files or personal health data.
