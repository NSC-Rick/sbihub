"""
Financial outcome comparison for the Model Comparison workspace.

Each model is evaluated independently with the V1 ``build_model``
calculation engine — no formulas are re-implemented here. Outputs are
then aligned under documented comparison rules:

- **Same time mode, same length:** compared period-by-period.
- **Same time mode, different lengths:** compared over the common
  horizon (``min(periods_a, periods_b)``); a warning and a rule entry
  are recorded.
- **Monthly vs annual:** the monthly model is aggregated to years and
  compared on an annual basis; a warning is recorded. Flow metrics are
  summed within each year; ``ending_cash`` uses the year-end balance;
  margin/DSCR ratios are re-derived from the aggregated flows.
- **Partial final year:** when a monthly model's horizon does not divide
  evenly into 12-month years, the last year is partial and flagged.

Metric definitions follow the V1 statements: revenue/gross
profit/opex/EBITDA/net income come from the P&L (which includes direct
labor in COGS and depreciation/taxes), cash metrics from the cash flow
statement, and debt service/interest from the loan schedule.
"""
from typing import Any, Dict, List, Optional, Tuple

from ..engine.model import build_model
from .schema import (
    KIND_CURRENCY,
    KIND_PERCENT,
    KIND_RATIO,
    MetricComparison,
    OutcomeView,
)

# (key, label, kind, aggregation, (output_key, column))
_BASE_METRICS = [
    ("revenue", "Revenue", KIND_CURRENCY, "sum", ("pnl_statement", "revenue")),
    ("gross_profit", "Gross Profit", KIND_CURRENCY, "sum", ("pnl_statement", "gross_profit")),
    ("payroll", "Payroll", KIND_CURRENCY, "sum", ("payroll_df", "total")),
    ("operating_expenses", "Operating Expenses", KIND_CURRENCY, "sum", ("pnl_statement", "operating_expenses")),
    ("ebitda", "Operating Profit (EBITDA)", KIND_CURRENCY, "sum", ("pnl_statement", "ebitda")),
    ("interest_expense", "Interest Expense", KIND_CURRENCY, "sum", ("loan_schedule", "interest")),
    ("net_income", "Net Income", KIND_CURRENCY, "sum", ("pnl_statement", "net_income")),
    ("operating_cash_flow", "Operating Cash Flow", KIND_CURRENCY, "sum", ("cash_flow_statement", "operating_cash_flow")),
    ("net_cash_flow", "Net Cash Flow", KIND_CURRENCY, "sum", ("cash_flow_statement", "net_cash_flow")),
    ("debt_service", "Debt Service", KIND_CURRENCY, "sum", ("loan_schedule", "payment")),
    ("ending_cash", "Ending Cash", KIND_CURRENCY, "last", ("cash_flow_statement", "ending_cash")),
]

# Derived metrics: (key, label, kind, numerator_key, denominator_key)
_DERIVED_METRICS = [
    ("gross_margin", "Gross Margin", KIND_PERCENT, "gross_profit", "revenue"),
    ("dscr", "Debt Service Coverage (DSCR)", KIND_RATIO, "ebitda", "debt_service"),
]

_MONTHS_PER_YEAR = 12


def evaluate_model(model_inputs: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Run the V1 calculation engine on a model_inputs dict.

    Returns:
        ``(outputs, error)`` — ``outputs`` is the ``build_model`` result
        on success (``None`` on failure); ``error`` is a human-readable
        message or ``None``.
    """
    try:
        return build_model(model_inputs), None
    except Exception as exc:  # engine errors surface to the user, not a crash
        return None, f"The model could not be calculated: {exc}"


def _num(value: Any) -> Optional[float]:
    """Convert a pandas/numpy scalar to a JSON-safe float (NaN -> None)."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result == result and abs(result) != float("inf") else None


def extract_base_series(outputs: Dict[str, Any]) -> Dict[str, List[Optional[float]]]:
    """Pull per-period base metric series out of a ``build_model`` result."""
    series: Dict[str, List[Optional[float]]] = {}
    for key, _label, _kind, _agg, (out_key, column) in _BASE_METRICS:
        df = outputs.get(out_key)
        if df is None or column not in getattr(df, "columns", []):
            series[key] = []
        else:
            series[key] = [_num(v) for v in df[column].tolist()]
    return series


def _aggregate(values: List[Optional[float]], chunk: int, method: str) -> List[Optional[float]]:
    """Aggregate a per-period series into ``chunk``-sized groups."""
    result: List[Optional[float]] = []
    for start in range(0, len(values), chunk):
        group = [v for v in values[start:start + chunk] if v is not None]
        if not group:
            result.append(None)
        elif method == "last":
            result.append(group[-1])
        elif method == "mean":
            result.append(sum(group) / len(group))
        else:  # 'sum'
            result.append(sum(group))
    return result


def _safe_ratio(num: Optional[float], den: Optional[float]) -> Optional[float]:
    if num is None or den is None or den == 0:
        return None
    return num / den


def _build_metrics(series_a: Dict[str, List[Optional[float]]],
                   series_b: Dict[str, List[Optional[float]]],
                   labels: List[str]) -> Dict[str, MetricComparison]:
    """Build MetricComparison entries for base + derived metrics."""
    metrics: Dict[str, MetricComparison] = {}

    for key, label, kind, agg, _src in _BASE_METRICS:
        va = series_a.get(key, [])[:len(labels)]
        vb = series_b.get(key, [])[:len(labels)]
        diff, pct = _diff_series(va, vb)
        metrics[key] = MetricComparison(
            key=key, label=label, kind=kind, agg=agg,
            period_labels=list(labels),
            values_a=va, values_b=vb, diff=diff, pct_diff=pct,
        )

    for key, label, kind, num_key, den_key in _DERIVED_METRICS:
        va = [
            _safe_ratio(n, d)
            for n, d in zip(series_a.get(num_key, []), series_a.get(den_key, []))
        ][:len(labels)]
        vb = [
            _safe_ratio(n, d)
            for n, d in zip(series_b.get(num_key, []), series_b.get(den_key, []))
        ][:len(labels)]
        diff, _pct = _diff_series(va, vb)
        metrics[key] = MetricComparison(
            key=key, label=label, kind=kind, agg="ratio",
            period_labels=list(labels),
            values_a=va, values_b=vb, diff=diff, pct_diff=[None] * len(labels),
        )

    return metrics


def _diff_series(va: List[Optional[float]],
                 vb: List[Optional[float]]) -> Tuple[List[Optional[float]], List[Optional[float]]]:
    diff: List[Optional[float]] = []
    pct: List[Optional[float]] = []
    for a, b in zip(va, vb):
        if a is None or b is None:
            diff.append(None)
            pct.append(None)
            continue
        d = b - a
        diff.append(d)
        pct.append(d / abs(a) if a != 0 else None)
    return diff, pct


def compare_outcomes(outputs_a: Dict[str, Any], inputs_a: Dict[str, Any],
                     outputs_b: Dict[str, Any], inputs_b: Dict[str, Any]
                     ) -> Tuple[Optional[OutcomeView], Optional[OutcomeView], List[str], List[str]]:
    """
    Align and compare two models' financial outcomes.

    Returns:
        ``(periodic_view, annual_view, warnings, rules_applied)``.
        ``periodic_view`` is ``None`` when comparison is only meaningful
        at annual level (mixed modes) or when both models are annual.
    """
    warnings: List[str] = []
    rules: List[str] = []

    mode_a = inputs_a.get("time_mode", "monthly")
    mode_b = inputs_b.get("time_mode", "monthly")
    periods_a = int(inputs_a.get("periods") or 0)
    periods_b = int(inputs_b.get("periods") or 0)

    base_a = extract_base_series(outputs_a)
    base_b = extract_base_series(outputs_b)

    if mode_a != mode_b:
        # Mixed modes: aggregate the monthly side to annual basis.
        warnings.append(
            "The models use different time modes "
            f"({mode_a} vs {mode_b}). Comparison is shown on an annual basis "
            "— monthly results are summed into years."
        )
        rules.append(
            "Mixed time modes: monthly flows summed to years; ending cash "
            "uses each year-end balance; margins and DSCR re-derived from "
            "aggregated flows."
        )
        monthly_a = mode_a == "monthly"
        annual_a = _annualize(base_a, periods_a, monthly_a)
        annual_b = _annualize(base_b, periods_b, monthly_a is False)
        years = min(len(annual_a.get("revenue", [])), len(annual_b.get("revenue", [])))
        if years == 0:
            return None, None, warnings + ["No overlapping forecast periods to compare."], rules
        if len(annual_a.get("revenue", [])) != len(annual_b.get("revenue", [])):
            warnings.append(
                f"Forecast lengths differ — comparison covers the first {years} "
                f"year{'s' if years != 1 else ''} only."
            )
            rules.append(f"Common horizon rule: compared over {years} shared year(s).")
        labels = [f"Year {i + 1}" for i in range(years)]
        notes = _partial_year_notes(periods_a, periods_b, monthly_a, years)
        view = OutcomeView(
            basis="annual", period_labels=labels,
            metrics=_build_metrics(annual_a, annual_b, labels),
            notes=notes,
        )
        warnings.extend(notes)
        return None, view, warnings, rules

    # Same time mode.
    horizon = min(periods_a, periods_b,
                  len(base_a.get("revenue", [])), len(base_b.get("revenue", [])))
    if horizon == 0:
        return None, None, ["No overlapping forecast periods to compare."], rules

    if periods_a != periods_b:
        warnings.append(
            f"Forecast lengths differ ({periods_a} vs {periods_b} periods). "
            f"Comparison covers the first {horizon} shared "
            f"{'months' if mode_a == 'monthly' else 'years'}."
        )
        rules.append(f"Common horizon rule: compared over {horizon} shared period(s).")

    if mode_a == "annual":
        labels = [f"Year {i + 1}" for i in range(horizon)]
        view = OutcomeView(
            basis="annual", period_labels=labels,
            metrics=_build_metrics(base_a, base_b, labels),
        )
        return None, view, warnings, rules

    # Monthly basis.
    period_labels = [f"Month {i + 1}" for i in range(horizon)]
    periodic = OutcomeView(
        basis="monthly", period_labels=period_labels,
        metrics=_build_metrics(base_a, base_b, period_labels),
    )

    annual_a = _annualize(base_a, horizon, True)
    annual_b = _annualize(base_b, horizon, True)
    n_years = min(len(annual_a.get("revenue", [])), len(annual_b.get("revenue", [])))
    year_labels = [f"Year {i + 1}" for i in range(n_years)]
    notes = _partial_year_notes(horizon, horizon, True, n_years)
    annual = OutcomeView(
        basis="annual", period_labels=year_labels,
        metrics=_build_metrics(annual_a, annual_b, year_labels),
        notes=notes,
    )
    warnings.extend(notes)
    rules.append("Monthly results are also aggregated to annual totals "
                 "(flows summed, ending cash at year-end, ratios re-derived).")
    return periodic, annual, warnings, rules


def _annualize(base: Dict[str, List[Optional[float]]], periods: int,
               is_monthly: bool) -> Dict[str, List[Optional[float]]]:
    """Aggregate a monthly base series dict to annual basis (no-op if annual)."""
    if not is_monthly:
        return {k: v for k, v in base.items()}
    agg_map = {key: agg for key, _l, _k, agg, _s in _BASE_METRICS}
    return {
        key: _aggregate(values, _MONTHS_PER_YEAR, agg_map.get(key, "sum"))
        for key, values in base.items()
    }


def _partial_year_notes(periods_a: int, periods_b: int, monthly_a: bool,
                        n_years: int) -> List[str]:
    """Flag partial final years when a monthly horizon isn't a whole year."""
    notes: List[str] = []
    for label, periods, is_monthly in (
        ("Model A", periods_a, monthly_a),
        ("Model B", periods_b, monthly_a is False),
    ):
        if is_monthly and periods % _MONTHS_PER_YEAR != 0:
            covered = min(periods, n_years * _MONTHS_PER_YEAR)
            remainder = covered % _MONTHS_PER_YEAR
            if remainder:
                notes.append(
                    f"{label}'s final compared year covers only "
                    f"{remainder} month{'s' if remainder != 1 else ''} (partial year)."
                )
    return notes
