# Third-party license review — PARTIAL / release NO-GO

This is an evidence log, **not** legal clearance or permission to redistribute model weights.

| Component | Version / model | Upstream evidence | Status / follow-up |
|---|---|---|---|
| QVAC SDK | `@qvac/sdk@0.22.0` | [npm package v0.22.0](https://www.npmjs.com/package/@qvac/sdk/v/0.22.0) identifies Apache-2.0; [official QVAC repository](https://github.com/tetherto/qvac) also labels source Apache-2.0 | **LICENSE IDENTIFIED**. Preserve notices; inspect exact package contents, native components and transitive licenses before redistribution |
| Model weights | `LLAMA_3_2_1B_INST_Q4_0` | [QVAC registry model-license mapping](https://github.com/tetherto/qvac/blob/main/packages/registry-server/README.md) lists `llama3.2` as Llama 3.2 Community License; [Meta terms](https://llama.meta.com/llama3_2/license/) | **REVIEW REQUIRED**. Confirm exact weight source, attribution, acceptable use and redistribution terms; do not upload weights |
| Direct/transitive dependencies | `package-lock.json` | Dependency list is in lockfile; [QVAC upstream license exceptions](https://github.com/tetherto/qvac/blob/main/.github/license-allowlist.yml) illustrate separate package-level review | **PENDING**. Inventory notices and license exceptions |
| Application code | AI Missy Offline | Private repository; no project-wide redistribution license independently reviewed | **PENDING**. Decide project license only after clearance |

## SDK runtime compatibility

Official [QVAC JS/TS SDK docs](https://docs.qvac.tether.io/sdk/js-ts-sdk/) list Node >=22.17 for JS/TS SDK usage. The [0.22.0 release notes](https://qvac.tether.io/changelog/sdk-v0-22-0) specify Node ^22.21.0 or >=24.9.0 for `qvac bundle` / bare-pack. Do not confuse the packaging-specific requirement with all SDK usage.

## Release policy

No model weights or raw patient/host evidence in Git. The SDK license alone does **not** clear model weights or every bundled native dependency. Public release and DoraHacks submission remain **NO_GO** until other gates and organizer deadline are reviewed.
