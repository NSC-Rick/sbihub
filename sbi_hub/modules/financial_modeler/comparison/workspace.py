"""
Model Comparison workspace — Streamlit UI.

A dedicated workspace inside the Financial Modeler app, reached via the
"Compare Models" sidebar action. It is strictly read-only with respect
to the active model: uploaded files are parsed into plain dicts and the
current model is only snapshotted — nothing is written back to the
model's session keys (workspace keys are ``mc_``-prefixed).

Workflow: choose a comparison mode → load the models → validate → run
the comparison → review the summary, assumption changes, and financial
outcome differences.
"""
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..utils.formatters import safe_currency, safe_percentage, safe_ratio
from .diff import format_assumption_value
from .engine import compare_models
from .loader import parse_model_file, snapshot_current_model
from .schema import (
    KIND_CURRENCY,
    KIND_PERCENT,
    KIND_RATIO,
    SOURCE_CURRENT_SESSION,
    SOURCE_UPLOADED_FILE,
    STATUS_ADDED,
    STATUS_LABELS,
    STATUS_MODIFIED,
    STATUS_REMOVED,
    STATUS_UNCHANGED,
    ComparisonResult,
)

MODE_CURRENT_VS_FILE = "current_vs_file"
MODE_TWO_FILES = "two_files"

_STATUS_ORDER = [STATUS_MODIFIED, STATUS_ADDED, STATUS_REMOVED, STATUS_UNCHANGED]
_STATUS_ICONS = {
    STATUS_MODIFIED: "✏️",
    STATUS_ADDED: "➕",
    STATUS_REMOVED: "➖",
    STATUS_UNCHANGED: "✓",
}

# Metrics shown in the headline "totals over the compared horizon" table.
_HEADLINE_METRICS = [
    "revenue", "gross_profit", "operating_expenses", "ebitda",
    "net_income", "operating_cash_flow", "debt_service", "ending_cash",
    "gross_margin", "dscr",
]


def render():
    """Render the Model Comparison workspace."""
    _render_sidebar()

    st.title("⚖️ Compare Models")
    st.caption(
        "See how two models differ — assumptions and results — side by side. "
        "Comparing never changes your active model."
    )

    mode = st.radio(
        "What would you like to compare?",
        options=(MODE_CURRENT_VS_FILE, MODE_TWO_FILES),
        format_func=lambda m: (
            "My current model vs a saved model"
            if m == MODE_CURRENT_VS_FILE else
            "Two saved model files"
        ),
        horizontal=True,
        key="mc_mode",
    )

    # Switching modes invalidates a stale result.
    if st.session_state.get("mc_last_mode") != mode:
        st.session_state["mc_last_mode"] = mode
        st.session_state.pop("mc_result", None)

    if mode == MODE_CURRENT_VS_FILE:
        side_a, side_b = _panel_current_vs_file()
    else:
        side_a, side_b = _panel_two_files()

    st.divider()

    ready = side_a is not None and side_b is not None
    if st.button(
        "⚖️ Compare Models",
        type="primary",
        disabled=not ready,
        help="Load both models to enable comparison." if not ready else
             "Run the comparison — your active model is not changed.",
    ):
        inputs_a, kwargs_a = _resolve_side(side_a, "a")
        inputs_b, kwargs_b = _resolve_side(side_b, "b")
        with st.spinner("Comparing models…"):
            st.session_state["mc_result"] = compare_models(
                inputs_a, inputs_b, **kwargs_a, **kwargs_b
            )

    result = st.session_state.get("mc_result")
    if result is not None:
        st.divider()
        _render_result(result)


def _render_sidebar():
    """Workspace sidebar: identity + the way back to the modeler."""
    st.sidebar.title("Financial Modeler")
    if st.sidebar.button(
        "← Back to Financial Modeler",
        use_container_width=True,
        help="Return to your model — nothing is changed or lost.",
    ):
        st.session_state["fm_workspace"] = "modeler"
        st.session_state["_scroll_to_top"] = True
        st.rerun()
    st.sidebar.divider()
    st.sidebar.caption(
        "**Model Comparison workspace.** Compare assumptions and outcomes "
        "between your current model and saved model files. Your active "
        "model is read-only here."
    )


# ---------------------------------------------------------------------------
# Model selection panels
# ---------------------------------------------------------------------------

def _panel_current_vs_file():
    """Mode B: current session model (read-only) vs one uploaded file."""
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Model A — Current model")
        snap = snapshot_current_model(st.session_state)
        _model_card(snap, "Active session (unsaved changes included)")
        st.caption("The model you are working on right now. It is only read — never changed.")
        side_a = ("current", snap)

    with col_b:
        st.subheader("Model B — Saved file")
        side_b = _uploader("mc_file_b", "Upload a saved model (.json)")

    return side_a, side_b


def _panel_two_files():
    """Mode A: two uploaded model files."""
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Model A — Original")
        side_a = _uploader("mc_file_a", "Upload the original model (.json)")

    with col_b:
        st.subheader("Model B — Comparison")
        side_b = _uploader("mc_file_b", "Upload the comparison model (.json)")

    return side_a, side_b


def _uploader(key: str, label: str):
    """Render a file uploader + validation; return ``(inputs, filename)``."""
    uploaded = st.file_uploader(label, type=["json"], key=key)
    if uploaded is None:
        return None

    inputs, errors = parse_model_file(uploaded.getvalue(), uploaded.name)
    if errors:
        for err in errors:
            st.error(err)
        return None

    _model_card(inputs, uploaded.name)
    return (inputs, uploaded.name)


def _model_card(inputs: dict, source_label: str):
    """Compact summary of a loaded model."""
    name = inputs.get("scenario_name") or "Unnamed model"
    mode = inputs.get("time_mode", "monthly")
    periods = inputs.get("periods", 0)
    horizon = (
        f"{periods} months ({periods // 12} yr)"
        if mode == "monthly" else f"{periods} years"
    )
    st.success(
        f"**{name}**  \n"
        f"{source_label} · {mode} · {horizon}  \n"
        f"{len(inputs.get('revenue_streams') or [])} revenue stream(s) · "
        f"{len(inputs.get('payroll_roles') or [])} payroll role(s) · "
        f"{len(inputs.get('opex_items') or [])} expense item(s)"
    )


def _resolve_side(side, side_letter: str):
    """Turn a selection-panel value into ``(inputs, compare_kwargs)``."""
    if side[0] == "current":
        # Snapshot at click time so latest edits are used.
        inputs = snapshot_current_model(st.session_state)
        kwargs = {
            f"label_{side_letter}": "Current Model",
            f"source_{side_letter}": SOURCE_CURRENT_SESSION,
        }
    else:
        inputs, filename = side
        kwargs = {
            f"label_{side_letter}": f"Model {side_letter.upper()}",
            f"source_{side_letter}": SOURCE_UPLOADED_FILE,
            f"filename_{side_letter}": filename,
        }
    return inputs, kwargs


# ---------------------------------------------------------------------------
# Result rendering
# ---------------------------------------------------------------------------

def _render_result(result: ComparisonResult):
    for warning in result.warnings:
        st.warning(warning)
    for error in result.errors:
        st.error(error)

    tab_summary, tab_assump, tab_outcomes, tab_details = st.tabs([
        "📋 Summary",
        "🔍 Assumption Changes",
        "📈 Financial Outcomes",
        "🧾 Details & Export",
    ])

    with tab_summary:
        _render_summary(result)
    with tab_assump:
        _render_assumptions(result)
    with tab_outcomes:
        _render_outcomes(result)
    with tab_details:
        _render_details(result)


def _render_summary(result: ComparisonResult):
    a, b = result.model_a, result.model_b

    def _desc(d):
        source = (
            "Current session" if d.source == SOURCE_CURRENT_SESSION
            else d.filename or "Uploaded file"
        )
        mode = d.time_mode or "—"
        periods = d.periods if d.periods is not None else "—"
        return [
            source,
            d.scenario_name or "Unnamed model",
            d.platform_version or "—",
            mode,
            str(periods),
            str(d.revenue_stream_count),
            str(d.payroll_role_count),
            str(d.opex_item_count),
        ]

    st.subheader("Models compared")
    desc = pd.DataFrame({
        "": ["Source", "Model name", "Platform version", "Time mode",
             "Forecast periods", "Revenue streams", "Payroll roles",
             "Expense items"],
        a.label: _desc(a),
        b.label: _desc(b),
    })
    st.dataframe(desc, hide_index=True, use_container_width=True)

    st.subheader("What changed")
    cols = st.columns(4)
    cols[0].metric("✏️ Modified", result.counts.get(STATUS_MODIFIED, 0))
    cols[1].metric("➕ Added", result.counts.get(STATUS_ADDED, 0))
    cols[2].metric("➖ Removed", result.counts.get(STATUS_REMOVED, 0))
    cols[3].metric("✓ Unchanged", result.counts.get(STATUS_UNCHANGED, 0))

    view = result.annual or result.periodic
    if view is not None:
        st.subheader("Headline results over the compared horizon")
        st.caption(f"Basis: {view.basis} · {len(view.period_labels)} period(s)")
        rows = []
        for key in _HEADLINE_METRICS:
            metric = view.metrics.get(key)
            if metric is None:
                continue
            a_tot, b_tot = _metric_totals(view, metric)
            rows.append({
                "Metric": metric.label,
                a.label: _fmt_metric(a_tot, metric.kind),
                b.label: _fmt_metric(b_tot, metric.kind),
                "Change": _fmt_metric(
                    None if (a_tot is None or b_tot is None) else b_tot - a_tot,
                    metric.kind, signed=True),
                "Change %": _fmt_pct(
                    None if (a_tot in (None, 0) or b_tot is None)
                    else (b_tot - a_tot) / abs(a_tot)),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True,
                     use_container_width=True)
    else:
        st.info("Financial outcome comparison is unavailable for these models.")


def _metric_totals(view, metric):
    """Total a metric over the compared horizon, honoring its aggregation."""
    def _total(values):
        vals = [v for v in values if v is not None]
        if not vals:
            return None
        if metric.agg == "last":
            return vals[-1]
        return sum(vals)

    if metric.key == "gross_margin":
        gp = view.metrics["gross_profit"]
        rev = view.metrics["revenue"]
        a_gp, a_rev = _total(gp.values_a), _total(rev.values_a)
        b_gp, b_rev = _total(gp.values_b), _total(rev.values_b)
        return (
            a_gp / a_rev if a_rev else None,
            b_gp / b_rev if b_rev else None,
        )
    if metric.key == "dscr":
        eb = view.metrics["ebitda"]
        ds = view.metrics["debt_service"]
        a_eb, a_ds = _total(eb.values_a), _total(ds.values_a)
        b_eb, b_ds = _total(eb.values_b), _total(ds.values_b)
        return (
            a_eb / a_ds if a_ds else None,
            b_eb / b_ds if b_ds else None,
        )
    return _total(metric.values_a), _total(metric.values_b)


def _render_assumptions(result: ComparisonResult):
    st.subheader("Assumption differences")
    st.caption(
        "Every input compared. Values shown as Model A → Model B; "
        "Change % is relative to Model A."
    )

    selected = st.multiselect(
        "Show statuses",
        options=_STATUS_ORDER,
        default=[STATUS_MODIFIED, STATUS_ADDED, STATUS_REMOVED],
        format_func=lambda s: f"{_STATUS_ICONS[s]} {STATUS_LABELS[s]}",
        key="mc_status_filter",
    )
    changes = [c for c in result.assumption_changes if c.status in selected]

    if not changes:
        st.info("No assumptions match the selected statuses.")
        return

    # Grouped by category, group order follows first appearance.
    groups = {}
    for change in changes:
        groups.setdefault(change.group, []).append(change)

    a_label = result.model_a.label
    b_label = result.model_b.label

    for group, group_changes in groups.items():
        n = len(group_changes)
        with st.expander(f"{group} ({n})", expanded=True):
            rows = []
            for c in group_changes:
                rows.append({
                    "Assumption": c.label,
                    "Status": f"{_STATUS_ICONS[c.status]} {STATUS_LABELS[c.status]}",
                    a_label: format_assumption_value(
                        c.value_a, c.path, c.path.rsplit(".", 1)[-1]),
                    b_label: format_assumption_value(
                        c.value_b, c.path, c.path.rsplit(".", 1)[-1]),
                    "Change": _fmt_change(c),
                    "Change %": _fmt_pct(c.pct_diff),
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True,
                         use_container_width=True)


def _fmt_change(change) -> str:
    if change.abs_diff is None:
        if change.details:
            # Entity added/removed — summarize its fields.
            parts = [
                f"{k}={format_assumption_value(v, '', str(k))}"
                for k, v in list(change.details.items())[:4]
            ]
            suffix = ", …" if len(change.details) > 4 else ""
            return "; ".join(parts) + suffix
        return "—"
    key = change.path.rsplit(".", 1)[-1]
    formatted = format_assumption_value(abs(change.abs_diff), change.path, key)
    sign = "+" if change.abs_diff > 0 else "−"
    return f"{sign}{formatted}"


def _render_outcomes(result: ComparisonResult):
    st.subheader("Financial outcome comparison")
    st.caption(
        "Each model was calculated independently with the Financial "
        "Modeler's own engine — figures match what you'd see on the "
        "Review page."
    )

    views = []
    if result.annual is not None:
        views.append(("Annual", result.annual))
    if result.periodic is not None:
        views.append(("Monthly", result.periodic))
    if not views:
        st.info("Financial outcome comparison is unavailable for these models.")
        return

    basis_label = st.radio(
        "View", options=[v[0] for v in views], horizontal=True,
        key="mc_outcome_basis",
    )
    if basis_label not in dict(views):
        basis_label = views[0][0]
    view = dict(views)[basis_label]

    metrics = list(view.metrics.values())
    chosen = st.selectbox(
        "Metric", options=[m.key for m in metrics],
        format_func=lambda k: view.metrics[k].label,
        key="mc_outcome_metric",
    )
    metric = view.metrics.get(chosen, metrics[0])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=metric.period_labels, y=metric.values_a,
        mode="lines+markers", name=result.model_a.label,
    ))
    fig.add_trace(go.Scatter(
        x=metric.period_labels, y=metric.values_b,
        mode="lines+markers", name=result.model_b.label,
    ))
    fig.update_layout(
        yaxis_title=metric.label,
        xaxis_title="Period",
        legend_title="Model",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    rows = []
    for i, period in enumerate(metric.period_labels):
        rows.append({
            "Period": period,
            result.model_a.label: _fmt_metric(metric.values_a[i], metric.kind),
            result.model_b.label: _fmt_metric(metric.values_b[i], metric.kind),
            "Change": _fmt_metric(metric.diff[i], metric.kind, signed=True),
            "Change %": _fmt_pct(metric.pct_diff[i]),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True,
                 use_container_width=True)

    st.download_button(
        f"Download {metric.label} comparison (CSV)",
        data=pd.DataFrame({
            "period": metric.period_labels,
            result.model_a.label: metric.values_a,
            result.model_b.label: metric.values_b,
            "change": metric.diff,
            "change_pct": metric.pct_diff,
        }).to_csv(index=False),
        file_name=f"comparison_{metric.key}_{view.basis}.csv",
        mime="text/csv",
    )


def _render_details(result: ComparisonResult):
    st.subheader("How this comparison was made")

    st.markdown("**Comparison rules applied**")
    rules = [
        "Each model is calculated independently using the Financial "
        "Modeler's unchanged V1 engine — no formulas are duplicated.",
        "Only overlapping forecast periods are compared (common horizon).",
        "Assumptions are matched by name for revenue streams, payroll "
        "roles, and expense items; everything else is matched by field.",
    ] + result.rules_applied
    for rule in rules:
        st.markdown(f"- {rule}")

    if result.warnings:
        st.markdown("**Warnings**")
        for warning in result.warnings:
            st.markdown(f"- {warning}")

    st.markdown(
        "**Structured output** — the full result below is the traceable "
        "record consumed by the comparison workspace and by future "
        "decision-support modules."
    )
    st.download_button(
        "Download comparison result (JSON)",
        data=json.dumps(result.to_dict(), indent=2),
        file_name="model_comparison_result.json",
        mime="application/json",
    )
    with st.expander("Preview result JSON"):
        st.json(result.to_dict())


def _fmt_metric(value, kind: str, signed: bool = False) -> str:
    if value is None:
        return "—"
    prefix = "+" if signed and value > 0 else ""
    if kind == KIND_CURRENCY:
        return prefix + safe_currency(value)
    if kind == KIND_PERCENT:
        return prefix + safe_percentage(value)
    if kind == KIND_RATIO:
        return prefix + safe_ratio(value)
    return f"{prefix}{value:,.2f}"


def _fmt_pct(value) -> str:
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{safe_percentage(value)}"
