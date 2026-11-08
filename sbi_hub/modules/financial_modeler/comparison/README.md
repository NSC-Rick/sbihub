# Model Comparison Workspace (V2.1)

A dedicated workspace inside the Financial Modeler app for comparing two
models — assumption differences and financial outcome differences —
without touching the active model or any V1 calculation code.

## Architecture

```
comparison/
├── __init__.py      # public API: compare_models, parse_model_file,
│                    #   snapshot_current_model, result types
├── schema.py        # structured result dataclasses (+ to_dict)
├── loader.py        # JSON file parsing/validation; session snapshot
├── diff.py          # assumption diff engine (pure, no UI)
├── outcomes.py      # build_model evaluation + period alignment rules
├── engine.py        # compare_models orchestrator
└── workspace.py     # Streamlit UI (the only Streamlit-aware module)
```

Layering is strict: `schema`, `loader`, `diff`, `outcomes`, and `engine`
contain no Streamlit code and can be tested and reused headlessly.
`workspace.py` is the only UI module; `app.py` routes to it when
`st.session_state.fm_workspace == 'comparison'`.

## Data flow

1. **Load** — `parse_model_file` validates uploads with the same
   `validate_scenario_json` used by V1 "Load Model" (plain dicts; never
   written to session state). `snapshot_current_model` deep-copies the
   active session's inputs via `session_state_to_model_inputs`, plus the
   session-only working-capital keys the engine reads.
2. **Diff** — `diff_model_inputs` produces a flat list of
   `AssumptionChange` with traceable paths
   (e.g. `revenue_streams["Product Sales"].price`).
3. **Evaluate** — each model runs independently through the unchanged V1
   `build_model` engine. No formulas are duplicated.
4. **Align** — `compare_outcomes` applies documented rules and emits
   per-period aligned `MetricComparison` series on monthly and/or annual
   bases.
5. **Result** — `ComparisonResult` bundles descriptors, changes, views,
   warnings, rules, and errors; `to_dict()` is JSON-serializable.

## Comparison rules

- Scalars compare with `math.isclose` (rel/abs 1e-9). `abs_diff = B − A`;
  `pct_diff = (B − A)/|A|` as a decimal fraction, `None` when A is zero.
- Revenue streams, payroll roles, and opex items match as entities by
  `name`/`role`; renames appear as remove + add. Entities present on one
  side only produce a single added/removed entry whose `details` dict
  carries its fields.
- Lists of scalars (e.g. `seasonality.custom_weights`) compare
  element-wise; nested dicts recurse.
- Period alignment: same-mode models compare over `min(periods)` (common
  horizon, flagged); mixed monthly/annual models compare on an annual
  basis only (monthly flows summed, `ending_cash` at year-end, margins
  and DSCR re-derived from aggregated flows); partial final years are
  flagged.
- Outcome metric sources: revenue/gross profit/opex/EBITDA/net income
  from `pnl_statement` (includes direct labor in COGS, depreciation, and
  taxes); cash metrics from `cash_flow_statement`; debt service/interest
  from `loan_schedule`.

## Extensibility (V2.2+)

`ComparisonResult.to_dict()` is the consumption contract for planned
modules — Decision Insights (ranked drivers of outcome deltas),
Experiment Sandbox (edit-and-compare loops), and Decision Journal
(persisted comparison records). Those capabilities are intentionally not
implemented in V2.1 and are not exposed in the UI.

## Limitations

- Saved-JSON files do not store session-only keys (`business_stage`,
  `model_mode`, `working_capital_source`, `starting_*_balance`) — V1
  schema limitation. Comparing the current model against a saved file
  therefore flags those keys as "added" on the session side, and engine
  defaults apply to the file side.
- `build_model` errors are captured per side in `result.errors`; the
  assumption diff still renders when outcomes are unavailable.
