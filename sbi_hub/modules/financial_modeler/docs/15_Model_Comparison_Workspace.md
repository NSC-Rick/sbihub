# Model Comparison Workspace — V2.1

**Status:** shipped on `v2-dev` · **Scope:** comparison only — Decision
Insights, Experiment Sandbox, and Decision Journal are future phases.

## What it does

Adds a dedicated **Compare Models** workspace to the Financial Modeler.
Users can compare:

- **Two saved model files** — upload two Financial Modeler JSON files.
- **Current model vs a saved file** — the active session model (a
  read-only snapshot) against one uploaded JSON file.

The workspace shows:

1. **Summary** — model descriptors side by side, change counts
   (added/removed/modified/unchanged), and headline financial results
   over the compared horizon.
2. **Assumption Changes** — every input difference grouped by category
   (Revenue Streams, Payroll & Staffing, Operating Expenses, Financing,
   Capital Structure, Working Capital, Taxes & Depreciation,
   Seasonality & Ramp, Forecast & Configuration, and more), with Model A
   value, Model B value, absolute change, and percentage change.
3. **Financial Outcomes** — annual and (when applicable) monthly
   side-by-side results with charts for revenue, gross profit/margin,
   payroll, operating expenses, EBITDA, interest, net income, cash
   flows, ending cash, debt service, and DSCR.
4. **Details & Export** — the comparison rules applied, warnings, and a
   downloadable JSON of the full structured result.

## Entry point & navigation

- Sidebar button **"⚖️ Compare Models"** (below the page radio) switches
  `st.session_state.fm_workspace` to `'comparison'` and renders the
  workspace.
- **"← Back to Financial Modeler"** in the workspace sidebar returns to
  the modeler. All model session keys are untouched — the active model
  is preserved exactly as left.
- Workspace state uses `mc_`-prefixed session keys only.

## Architecture

New package `sbi_hub/modules/financial_modeler/comparison/`:

| Module | Role |
| --- | --- |
| `schema.py` | `ComparisonResult`, `AssumptionChange`, `MetricComparison`, `OutcomeView`, `ModelDescriptor` — all `to_dict()`-serializable |
| `loader.py` | `parse_model_file` (validates with V1 `validate_scenario_json`), `snapshot_current_model` (deep-copy via `session_state_to_model_inputs` + session-only keys) |
| `diff.py` | `diff_model_inputs` → flat `AssumptionChange` list; plain-English labels, groups, and value formatting |
| `outcomes.py` | `evaluate_model` (V1 `build_model` wrapper), metric extraction, period alignment + aggregation |
| `engine.py` | `compare_models` — single entry point for both modes |
| `workspace.py` | Streamlit UI; the only Streamlit-aware module |

`app.py` gained ~20 lines: a workspace-mode check and the sidebar
action. No existing page, calculation, export, or session code was
modified.

## Comparison rules (documented behavior)

- **Same mode, same length:** period-by-period.
- **Same mode, different lengths:** common horizon `min(periods)`;
  warning + rule recorded.
- **Monthly vs annual:** annual basis only; monthly flows summed per
  year, `ending_cash` = year-end balance, margins/DSCR re-derived from
  aggregated flows.
- **Partial final year** (monthly periods not divisible by 12): flagged.
- **Version differences:** warned when `platform_version` differs or is
  absent on one side.
- **Engine failure** on either side: captured in `result.errors`;
  assumption diff still renders.

## Limitations

- **Saved-file schema:** V1 JSON does not persist `business_stage`,
  `model_mode`, `working_capital_source`, or `starting_*_balance`.
  Current-vs-saved comparisons include these session keys on the current
  side (shown as "added" under *Business Stage & Session Settings*) so
  the current model is evaluated honestly; engine defaults apply to the
  file side.
- Uploaded files are compared as-is; hand-edited files may produce
  engine errors (captured, not fatal).
- Streamlit AppTest cannot script `st.file_uploader`, so upload flow
  coverage is via `parse_model_file` unit tests plus manual QA.

## Testing

42 new tests in `sbi_hub/modules/financial_modeler/tests/`:

- `test_comparison_diff.py` — statuses, entity matching, nested/indexed
  paths, tolerance, formatting (15 tests)
- `test_comparison_loader.py` — file validation, malformed input,
  session snapshot isolation (8 tests)
- `test_comparison_outcomes.py` — metric extraction, annual aggregation,
  horizon/mixed-mode/partial-year rules (11 tests)
- `test_comparison_engine.py` — `compare_models` end-to-end, warnings,
  JSON-serializable `to_dict()` (8 tests)

Full suite: **308 passed** (266-test V1 baseline unchanged; parity test
`test_fm_parity.py` green — no re-baseline was needed).

## Readiness for Decision Insights (V2.2)

- `ComparisonResult.to_dict()` is a stable, versioned
  (`engine_version: "2.1.0"`) JSON contract — suitable input for insight
  ranking, sandbox replay, and journal persistence.
- Every change is traceable (`path`, `group`, `entity`, raw + delta
  values); every outcome delta is period-aligned and labeled — enough
  structure to rank "which assumption drove which outcome" without
  re-running models.
- `loader`/`diff`/`outcomes` are Streamlit-free, so sandbox loops can
  mutate `model_inputs` dicts and re-call `compare_models` cheaply.
- Not yet provided (by design): per-assumption outcome attribution,
  scenario persistence, or journal storage — those belong to the
  Decision Insights / Experiment Sandbox / Decision Journal phases.
