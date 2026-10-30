# AI Missy Offline — Final Ship Guide

**Scope:** Windows localhost demonstration using QVAC on-device text intent extraction, synthetic fluid records and SQLite confirmation. Not a medical device, not clinically validated, not voice-enabled.

## 1. Download and unzip

Save `AI_Missy_Offline_FinalShip.zip` to Downloads and run in PowerShell:

```powershell
$zip = "$env:USERPROFILE\Downloads\AI_Missy_Offline_FinalShip.zip"
Expand-Archive -LiteralPath $zip -DestinationPath "$env:USERPROFILE\Downloads" -Force
Set-Location "$env:USERPROFILE\Downloads\AI_Missy_Offline_FinalShip"
```

## 2. Prepare with internet (required only once)

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\FINAL_WINDOWS_RUN.ps1 -Stage Diagnose
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\FINAL_WINDOWS_RUN.ps1 -Stage PrepareOnline
```

If installation/model preload fails, STOP and share the first error. Do not claim an offline demonstration.

## 3. Prove the real offline path

Disconnect Wi-Fi, Ethernet, VPN, hotspot and other network paths. Start a continuous screen recording showing disconnection. Then:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\FINAL_WINDOWS_RUN.ps1 -Stage VerifyOffline
```

The gate tests QVAC model load, text extraction, HTTP -> QVAC -> SQLite, and regression tests. **Host-observed PASS is not independent network attestation.** Review the generated `local-evidence/` files privately.

## 4. Demo and publish

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\FINAL_WINDOWS_RUN.ps1 -Stage Demo
```

Browse to http://127.0.0.1:8766. For GitHub identity/preflight only:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\FINAL_WINDOWS_RUN.ps1 -Stage PublishDryRun
```

To actually publish, review source and license, then run `scripts/publish-new-repo.ps1 -Publish` and complete its explicit prompts. This creates a **PUBLIC** repo; it is not run automatically. Confirm remote eligibility and submit on DoraHacks manually. Never upload real patient records, raw hardware logs or model cache.

## Disclosure

- QVAC SDK package pinned to `@qvac/sdk@0.22.0` in `package.json`; availability and runtime on your host must be verified during `npm install`.
- The model constant is `LLAMA_3_2_1B_INST_Q4_0`. Initial download requires internet.
- STT/TTS, OCR, individualized nutrition advice, medical predictions, and background reminders are **not implemented**.
- All patient data in this demo are synthetic.
