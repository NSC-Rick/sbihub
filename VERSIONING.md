# SBI Hub — Financial Modeler V1 / V2 Version Arrangement

Date established: 2026-11-08.

## V1 release baseline

- **Tag (immutable baseline):** `v1.0.0` → commit `44c68e3d19d0e0ce554ea9e2de8be3a1f09c1afa`
- **Production deployment:** Render service `sbi-hub`, branch `dev`, serving the tag's content.
- **Vendored FM source version:** upstream `NSC-Rick/FinanceModeler` @ `49f2a0c`
  (platform v0.9.3), plus SBI-local adaptations recorded in the tag message:
  package-qualified imports, `app.py` wrapped in `render()` with
  `set_page_config` moved to `fm_app.py`, the `custom_styles.py` light-theme
  guard, and the "Financial Modeler" title relabel.
- The standalone `FinanceModeler` repository is **not** a runtime dependency
  of SBI; it is preserved as-is upstream and must not be modified.

### Restoring V1

If a future release regresses, roll back by either:

1. **Render dashboard:** `sbi-hub` → *Manual Deploy* → deploy commit
   `44c68e3d19d0e0ce554ea9e2de8be3a1f09c1afa` (or select the previous
   successful deploy). No code changes needed.
2. **Git:** revert dev to the tag and push:
   `git revert --no-commit v1.0.0..dev && git commit -m "Rollback to v1.0.0" && git push origin dev`
   — or hard-reset only with team approval (rewrites shared history).

## V2 development branch

- **Branch:** `v2-dev`, created from the V1 baseline lineage.
- **Isolation:** the Render `sbi-hub` service is a single-service,
  single-branch deployment tracking `dev` (evidence: `main` is 7 commits
  behind and never deployed; every `dev` push redeployed). Commits on
  `v2-dev` therefore cannot reach production — no configuration change is
  required. Do NOT point the existing service at `v2-dev`.

### V2 preview deployment (recommended, optional)

For stakeholder review of V2 before promotion, create a **separate** Render
web service (free tier) tracking `v2-dev` with the same build/start commands
from `render.yaml`. It gets its own URL (e.g. `sbi-hub-v2.onrender.com`) and
its own 512 MB quota — the current two-process footprint already fits that
budget on production, so a preview is workable. It will sleep when idle
(free tier), so expect cold starts. This must be created in the Render
dashboard (or via API key); nothing in the repo needs to change.

### Promotion workflow (proposed)

1. V2 work lands on `v2-dev` (or feature branches merged into it).
2. Gate on every merge: full `pytest` run, including `tests/test_fm_parity.py`.
3. Preview QA on the `v2-dev` Render service.
4. Promotion = merge `v2-dev` → `dev` (PR reviewed), which auto-deploys.
   Before the first promotion, cut a `v2.0.0` tag after merge.
5. Rollback = the V1 restore procedure above.

## Test baseline (recorded 2026-11-08 on commit 44c68e3)

- **266 passed, 0 failed** (`pytest`, ~12s):
  - 209 vendored FM baseline tests (engine calculations, P&L / cash-flow /
    income statements, loan amortization, capital stack, scenario JSON
    save/load validation, Excel export)
  - 55 hub tests (module registry, branding, announcements, navigation,
    `?view=` deep links, FM standalone launch, serve.py routing)
  - 2 new parity tests (`tests/test_fm_parity.py`)
- **Calculation parity baseline:** `tests/baselines/fm_v1_baseline.json`
  stores a fixed synthetic scenario's complete `build_model` outputs
  (36 periods × 9 output structures, floats rounded to 6 decimals),
  outputs sha256 `a022f697fdf685af96601b1fb8968d445ea26c1876a1b9efd3227a14b618bd81`.
  `test_fm_parity.py` reruns the scenario and fails on any divergence —
  intentional engine changes in V2 require an explicit re-baseline.
- **Scenario JSON compatibility:** `validate_scenario_json` round-trips a
  generated scenario cleanly; the schema is unchanged, so existing saved
  JSON models remain compatible.
- **Production smoke check (2026-11-08):** hub renders new terminology and
  all 8 cards; `/fm` loads with title "Financial Modeler"; Financial
  Modeler and Business Valuation launch links present; WebSocket-driven
  render confirmed via real browser (Playwright). Note: free-tier cold
  starts can exceed 90 s on first hit.

## Risks / decisions requiring approval

1. **Vendored FM divergence:** the V1 copy carries SBI-local patches listed
   above; V2 development happens on that copy, so upstream FM fixes will
   not flow in automatically (per the source-sync decision — upstream is
   preserved, not synchronized).
2. **`report_view.py` delta:** our title relabel renamed the report header/
   footer; upstream's rename commit did not touch that file. Local-only
   change — keep it (consistent) unless V2 re-aligns with upstream.
3. **Preview service quota:** two live free-tier services each get 512 MB;
   if Render ever enforces an account-level cap, the preview may need a
   paid tier or scheduled availability.
4. **Shared session file:** FM autosave uses `~/.finlite_session.json` —
   a V2 preview service has its own filesystem, so V1 and V2 sessions do
   not collide.
5. **Tag protection:** `v1.0.0` is an annotated git tag; immutability is by
   convention (don't force-push it). GitHub tag protection can be enabled
   in repo settings if stronger guarantees are wanted.
