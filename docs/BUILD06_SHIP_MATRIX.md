# Build 06 — final ship matrix

| Gate | Status | Proof / blocker |
|---|---|---|
| Python + HTTP tests | PASS locally | `python -m unittest discover -s tests -q` (52 tests, including six mocked-QVAC HTTP tests) |
| JavaScript syntax | PASS locally | `node --check` on QVAC scripts and UI; not native QVAC inference |
| Source integrity | PASS locally | `docs/BUILD06_RELEASE_RECEIPT.json` SHA256 manifest |
| QVAC Windows requirements | PENDING | Node version, Vulkan >=1.4, disk and model load on target laptop |
| QVAC model preload | PENDING | Actual online `npm run model:preload` success |
| QVAC genuinely offline | PENDING | Offline `VerifyOffline` receipt + continuous uncut recording |
| SQLite confirmation/replay | PASS in mock HTTP tests | Must be repeated in real disconnected browser demo |
| Voice input and TTS | NOT IMPLEMENTED | Never claim voice functionality in submission |
| Browser reminder | Implemented, limited | Tab must stay open; not a background Windows reminder |
| Real clinical nutrition database | NOT IMPLEMENTED | Food card abstains from personalized portions |
| Independent GitHub repo | NOT CREATED | `scripts/publish-new-repo.ps1` requires Windows gh auth and user approval |
| Model/SDK license review | PENDING | Verify Meta Llama 3.2 and QVAC SDK license before publication |
| Remote participation eligibility | PENDING | Verify official organizer rules |
| Demo video | NOT RECORDED | Continuous offline video required |
| DoraHacks submission | NOT SUBMITTED | Submission receipt required |

**Code GO, Ship NO-GO.** Do not describe the app as clinically validated, voice-first implemented, fully offline proven, or submitted until the corresponding proof exists.
