# AI Missy — Real Demo Video Evidence Kit (Build 24)

**Status: Recording NOT STARTED. Host code gate not independently revalidated here.**

## Windows capture workflow
1. In a fresh Build24 worktree, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\video-evidence-preflight.ps1`. Review `local-evidence/video/VIDEO_EVIDENCE_MANIFEST.json`. If FAIL, fix code gate first.
2. Prepare isolated synthetic database before server startup:
   ```powershell
   $env:MISSY_DB_PATH = Join-Path (Get-Location) 'local-evidence\video\missy_synthetic_recording.sqlite3'
   $env:MISSY_PORT = '8766'
   py server.py
   ```
3. Open `http://127.0.0.1:8766`. Verify the synthetic demo banner. No real patient data.
4. Use OBS Studio or equivalent to record an uninterrupted segment: network state, Wi-Fi disconnection, real local QVAC inference, proposed action, manual confirmation, and refreshed persisted record. Dependencies/model must have been preloaded. Record failures as failures.
5. Capture a separate real safety rejection response. Do not show secrets.
6. Only show Build22 Export / Build23 Timeline as verified after code gate **and UI E2E** pass. Otherwise display PR marked `UNDER VALIDATION`.
7. Enter actual evidence filenames and outcomes in `local-evidence/video/SHOT_EVIDENCE_LOG.csv`. Raw footage stays local, outside Git.

## Timecoded 3:30 storyboard

| Scene | Time | Real capture | Claim |
|---|---|---|---|
| S01 | 00:00–00:18 | Opening/title | Concept |
| S02 | 00:18–00:40 | localhost UI and terminal | Actual demo |
| S03 | 00:40–01:00 | Disconnect Wi-Fi and continue | Retest |
| S04 | 01:00–01:30 | Log 200 ml, model output, confirm | Retest |
| S05 | 01:30–01:55 | Refresh persisted synthetic total | Retest |
| S06 | 01:55–02:20 | Actual safety rejection | Retest |
| S07 | 02:20–02:45 | Timeline/export or PR | Under validation unless UI verified |
| S08 | 02:45–03:10 | PAIR and ACE Health OS diagram | Future roadmap |
| S09 | 03:10–03:30 | Closing and repo | Branding |

## Claims and editing rules
- Keep `SYNTHETIC DEMO DATA` visible on product shots.
- No claim of clinical validation, medical-device status, individualized fluid targets, or production authorization.
- If QVAC fails while offline, show that honestly; do not use a mock response.
- Build23 code gate PASS alone does not establish offline QVAC or UI E2E PASS.
- Consent, encryption, clinical RBAC, patient identity and provider integrations remain future roadmap.
- Deliver 1920×1080, 30fps H.264 MP4 with English captions after actual editing.
- Keep raw footage and any secrets outside the public repository.
- Do not merge or deploy based on this video kit.

## Evidence files
`local-evidence/video/VIDEO_EVIDENCE_MANIFEST.json`, `SHOT_EVIDENCE_LOG.csv`, `build23_gate_console.log`, and original screen recordings stored locally.
