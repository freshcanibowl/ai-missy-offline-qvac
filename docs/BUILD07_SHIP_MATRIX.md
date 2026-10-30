# Build 07 — Evidence-gated ship matrix

| Gate | State in this delivery | Proof / limitation |
|---|---|---|
| Source tests | PASS in container | 57/57 Python tests; mocked HTTP tests explicitly not real inference |
| Node syntax | PASS in container | `node --check` only; native QVAC not run |
| Package integrity | PASS | ZIP test + SHA256 in delivery notes |
| Windows Node/Vulkan/RAM | PENDING | Run `Preflight` on user's Windows machine |
| Online model preload | PENDING | Run `PrepareOnline` |
| QVAC smoke and intent parsing while offline | PENDING | Real SDK receipt, adapter disconnection, uncut video |
| Real HTTP → QVAC → SQLite → replay | PENDING | **New Build07** `live_http_e2e.py` receipt, no mock |
| Browser demo and reminder | PENDING | Show on Windows with network disconnected; browser tab stays open |
| Model license | PENDING | Human review required; no bundled model |
| Remote/in-person eligibility | PENDING | Confirm with organizer |
| Public GitHub repository | NOT CREATED | Separate repo, explicit approval |
| DoraHacks submission | NOT SUBMITTED | Actual organizer confirmation required |

**Release decision: CODE PASS / SHIP NO-GO.** No actual Windows inference, video, GitHub push, or organizer submission has been completed by this delivery.
