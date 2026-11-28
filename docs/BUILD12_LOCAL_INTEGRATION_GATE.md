# Build12 — Daily Metabolic Journal Integration (Local Patch)

2026-11-08. Current status: **ISOLATED PATCH READY / GITHUB RUNTIME NOT INTEGRATED / NO CLINICAL USE**.

- A downloadable local patch (`AI_Missy_Build12_Integration_Patch.zip`) provides isolated `metabolic/daily_care.py`, `metabolic/plan_contract.py`, `metabolic/bridge.py`, 11 new tests and `apply_build12.py`.
- Installer requires an existing checkout with expected `server.py`/`core.py`, fails closed on version mismatch, copies a separate `metabolic` package, creates a backup and adds dedicated `/api/metabolic/*` routing. It does not modify the legacy fluid store, QVAC parser, or existing endpoint semantics.
- The local Build12 addon passed **11/11** unit tests. The patcher's structural compatibility was checked on a mock source fixture only, not on the actual Windows checkout. Independent Build11 suite **32/32** and Build09 **16/16** were also rerun locally; these are separate test runs, not an integrated mainline test.
- Real Windows local apply, entire original repository tests, QVAC offline inference and PAIR end-to-end handoff remain **PENDING**.
- Clinical plan submission remains `UNVERIFIED_REVIEW_REQUIRED`; no clinical targets become active. Proposed PAIR summary is always `NOT_SENT`. Synthetic-only input, no patient IDs and no real data allowed.
- This is a **documentation-only** GitHub commit. Main and production remain unchanged; PR remains DRAFT. Do not represent the zip as already installed in GitHub or deployed.

## Host acceptance
1. Apply patch on an isolated disposable feature-branch checkout with `py apply_build12.py --repo <local clone>`.
2. Run existing repo suite: `py -m unittest discover -s tests -v`.
3. Run Build12 addon tests in extracted zip via `py run_build12_tests.py`.
4. Validate old QVAC water logging and new journal via local HTTP. Document any conflicts or roll back from `server.py.pre_build12_backup`.
5. Only then consider porting reviewed code to feature branch in GitHub for full CI; no merge without evidence.
