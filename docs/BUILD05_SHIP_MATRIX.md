# Build 05 — Ship Matrix (truthful status)

| Gate | Status | Evidence needed |
|---|---|---|
| Source/test gates | Local PASS (Linux) | Test output and release SHA256 |
| Windows Node + Vulkan | PENDING | Windows preflight receipt |
| QVAC model preload | PENDING | Online model download receipt |
| QVAC true offline completion | PENDING | Host-observed JSONL, continuous video, manual inspection |
| QVAC extraction 200mL | PENDING | Verified host JSONL + 200mL in browser |
| Local persistence | PENDING Windows | Refresh with offline network; SQLite stays local |
| Food advisory | FAIL-CLOSED BY DESIGN | No patient-specific portions or numeric food claims |
| Browser reminder | PENDING Windows | Tab stays open; NOT background Windows alarm |
| GitHub repository | NOT CREATED | Public judge-readable repository and disclosure |
| Demo video | NOT RECORDED | One uncut video showing disconnected networks |
| Model licensing | PENDING | Human review of model and SDK license |
| Eligibility | PENDING | Organizer confirms remote/in-person participation |
| DoraHacks submission | NOT SUBMITTED | Official receipt URL |

**Decision: NO-GO for claims of completed offline demo or hackathon submission.**

Do not upload personal host identifiers, private health records, `.env`, `node_modules`, SQLite databases, or raw unredacted evidence to a public repository.
