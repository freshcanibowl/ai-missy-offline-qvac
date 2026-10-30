# Build 04 Ship Gate — evidence-based

| Gate | Required evidence | Current status |
|---|---|---|
| Local app code | Python unit + HTTP integration test output | PASS in isolated Linux environment (see response), not Windows |
| QVAC SDK integration | `@qvac/sdk@0.22.0` calls and parser | CODE PRESENT, actual model untested |
| SDK installation / model download | Windows npm install + preload output | NO-GO pending Windows |
| QVAC cold-load offline | Continuous video + `qvac-smoke-*.jsonl` | NO-GO pending Windows |
| QVAC structured extraction offline | 200 mL + `qvac-parse-*.jsonl` | NO-GO pending Windows |
| QVAC receipt validation | `qvac-verified-*.json` and exit code 0 | NO-GO pending Windows |
| User confirmation and persistence | Browser recording + refresh | NOT DEMONSTRATED ON WINDOWS |
| Reminder trigger | Continuous video, browser tab open | NOT DEMONSTRATED ON WINDOWS |
| Model license | Verify license and attribution for Llama 3.2 | PENDING |
| Eligibility | Confirm remote entry with organizer (in-person ambiguity) | PENDING |
| GitHub public source | Judge-accessible URL, clean history | NOT PUBLISHED |
| Demo video | Judge-accessible uncut offline proof | NOT RECORDED |
| DoraHacks | Submitted URL/receipt | NOT SUBMITTED |

**Current release decision: SHIP NO-GO.** Ship only after independent hardware/offline evidence and submission checklist are complete. The archive is a release candidate, not a completed entry.
