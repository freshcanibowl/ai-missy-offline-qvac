# AI Missy Offline — Ship Rescue / Windows-first

## Verified facts
- Code unit/integration tests execute locally without QVAC and are **not** real model evidence.
- QVAC `@qvac/sdk` 0.22.0 and model `LLAMA_3_2_1B_INST_Q4_0` are referenced by the code.
- This project currently has **text input**, not working STT/TTS/OCR. Browser tab must remain open for reminders.
- Food lookup intentionally abstains; no validated patient-specific food advice.
- Demo case is synthetic; no real clinical plan or patient information.
- Real Windows QVAC offline inference, video, GitHub and DoraHacks submission are **not verified**.

## Fastest path to a real result
1. Extract the ZIP. In PowerShell, `cd` into the extracted project.
2. `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\triage_windows.ps1`
3. If the Node version is too old, install Node 22.21+ or 24.9+ before retrying. Check Windows Vulkan 1.4.
4. While online: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_HERE_WINDOWS.ps1 -Phase PrepareOnline`
5. Disconnect all network interfaces, begin continuous video capture, and run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_HERE_WINDOWS.ps1 -Phase VerifyOffline`
6. If PASS, start `py server.py`, visit http://127.0.0.1:8766 and show the synthetic 200 mL workflow.
7. Run `py scripts/submission_preflight.py`; then review and explicitly publish using `scripts/publish-new-repo.ps1 -Publish` only if authorized.
8. Upload the *real* video and accessible repository link to the DoraHacks Build. Do not mark submitted until the portal confirms it.

## Troubleshooting
- `NODE_UNSUPPORTED`: upgrade Node; `node --version` must be compatible.
- `VULKANINFO` unavailable: Vulkan runtime is not proven; inspect GPU drivers/runtime. This alone does not mean inference is impossible.
- `MODEL_PRELOAD_FAILED`: retain network, inspect package installation/model download errors; do not attempt offline proof yet.
- `QVAC_PARSE_FAILED`: check actual model output and JSON schema; do not use a simulated response.
- `NETWORK_ADAPTER_STILL_UP`: verify adapter state; don't claim network isolation.
- `REAL_HTTP_QVAC_E2E_FAILED`: preserve logs locally and fix the real inference path.

## Privacy
`local-evidence/`, `node_modules/`, databases, recordings, and host logs are excluded from Git. Inspect any logs before sharing.
