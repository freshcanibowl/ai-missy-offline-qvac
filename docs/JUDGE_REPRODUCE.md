# Judge reproduction — AI Missy Offline × QVAC

1. Device: Windows 10/11 x64. Install Node version supported by QVAC SDK 0.22, Python 3.10+. Hardware compatibility and Vulkan are device-dependent.
2. `npm install` and `npm run model:preload` **while online**. The model and SDK are not bundled. Record the versions and license.
3. Disconnect every network adapter; show adapter status in one continuous video.
4. Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-offline-gate.ps1` and wait for `BUILD04_LOCAL_OFFLINE_GATE=PASS`.
5. With network still disconnected, run `py server.py` and visit `http://127.0.0.1:8766`.
6. Enter `Log 200 ml water`, click `Ask local QVAC`, confirm only if it extracts 200 mL. Verify synthetic total changes from 700 to 900 mL and persists on refresh.
7. Select Banana; observe `INSUFFICIENT_DATA` (the model cannot invent nutrient quantities). Set the 2-minute reminder; keep the browser tab open until due.
8. Note that text input, not STT/TTS, is implemented. No cloud inference or model fallback. Reminders are browser-tab dependent. The example is not medical advice.

**Network-dependent:** initial `npm install`, initial QVAC model download, optional GitHub publishing and clinical synchronization (not implemented). **Offline after provisioning:** local QVAC inference (pending proof), text input, SQLite, food abstention, browser-tab reminders.

The exact file paths for QVAC: `scripts/preload-model.mjs`, `scripts/offline-smoke.mjs`, `scripts/qvac-parse.mjs`.
