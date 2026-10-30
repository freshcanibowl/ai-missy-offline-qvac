# Build 03 — 90-second continuous offline demo (synthetic only)

1. **0–10 s:** Show Windows Wi-Fi/Ethernet disabled, PowerShell hardware/adapter status. No cuts around disconnect.
2. **10–30 s:** Run `npm run model:offline` and show real QVAC model load + generated text.
3. **30–50 s:** Run `node scripts/qvac-parse.mjs '{"text":"Log 200 ml water"}'`; show QVAC JSON extraction.
4. **50–70 s:** Start `py server.py`; open `http://127.0.0.1:8766`; ask QVAC to parse, confirm 200 mL; see 700 -> 900 mL.
5. **70–85 s:** Refresh; show 900 mL persists; check banana and display `INSUFFICIENT_DATA`; demonstrate reminder record.
6. **85–90 s:** Show README disclosure: synthetic data, no clinical claims, no STT/TTS, browser must stay open for reminders.

Note: cold-loading QVAC may exceed 90 s. Use a longer continuous recording if needed; do not hide startup latency.

### Evidence files

The Windows script writes `local-evidence/offline-*.txt` and `hardware-*.json`. Inspect for identifiers before sharing. They are excluded by `.gitignore`. Logs plus a video are supporting evidence, not a cryptographic proof that every network path was blocked.
