"""Tests for financial outcome comparison (engine eval + alignment rules)."""
import copy

import pytest

from sbi_hub.modules.financial_modeler.comparison.outcomes import (
    compare_outcomes,
    evaluate_model,
    extract_base_series,
)
from sbi_hub.modules.financial_modeler.engine.validation import (
    get_default_model_inputs,
)


@pytest.fixture
def inputs():
    return get_default_model_inputs()


@pytest.fixture
def outputs(inputs):
    result, error = evaluate_model(inputs)
    assert error is None
    return result


def test_evaluate_model_success(inputs):
    outputs, error = evaluate_model(inputs)
    assert error is None
    assert "pnl_statement" in outputs
    assert "cash_flow_statement" in outputs


def test_evaluate_model_failure_captured():
    outputs, error = evaluate_model({"time_mode": "monthly"})
    assert outputs is None
    assert error is not None


def test_extract_base_series(outputs):
    series = extract_base_series(outputs)
    assert len(series["revenue"]) == 36
    assert len(series["ending_cash"]) == 36
    assert series["revenue"][0] is not None


def test_identical_models_zero_diff(inputs, outputs):
    outputs2, _ = evaluate_model(copy.deepcopy(inputs))
    periodic, annual, warnings, rules = compare_outcomes(
        outputs, inputs, outputs2, inputs)

    assert annual is not None
    assert periodic is not None
    for metric in annual.metrics.values():
        assert all(d == 0 or d is None for d in metric.diff)
    for metric in periodic.metrics.values():
        assert all(d == 0 or d is None for d in metric.diff)


def test_annual_aggregation_sums_flows(inputs, outputs):
    periodic, annual, _, _ = compare_outcomes(
        outputs, inputs, outputs, inputs)

    assert annual.basis == "annual"
    assert len(annual.period_labels) == 3  # 36 months -> 3 years
    rev = annual.metrics["revenue"]
    monthly_rev = periodic.metrics["revenue"]
    assert abs(rev.values_a[0] - sum(monthly_rev.values_a[:12])) < 1e-6


def test_ending_cash_uses_year_end(inputs, outputs):
    _, annual, _, _ = compare_outcomes(outputs, inputs, outputs, inputs)
    ending_cash = annual.metrics["ending_cash"]
    # Year-end ending cash equals the December value of each year.
    monthly = extract_base_series(outputs)["ending_cash"]
    assert ending_cash.values_a[0] == monthly[11]
    assert ending_cash.values_a[1] == monthly[23]


def test_common_horizon_for_different_periods(inputs, outputs):
    short = copy.deepcopy(inputs)
    short["periods"] = 24
    outputs_short, _ = evaluate_model(short)

    periodic, annual, warnings, _ = compare_outcomes(
        outputs, inputs, outputs_short, short)

    assert len(periodic.period_labels) == 24
    assert len(annual.period_labels) == 2
    assert any("Forecast lengths differ" in w for w in warnings)


def test_mixed_modes_compare_annually(inputs, outputs):
    annual_inputs = copy.deepcopy(inputs)
    annual_inputs["time_mode"] = "annual"
    annual_inputs["periods"] = 3
    annual_outputs, err = evaluate_model(annual_inputs)
    assert err is None

    periodic, annual, warnings, rules = compare_outcomes(
        outputs, inputs, annual_outputs, annual_inputs)

    assert periodic is None
    assert annual is not None
    assert annual.basis == "annual"
    assert len(annual.period_labels) == 3
    assert any("different time modes" in w for w in warnings)
    assert rules


def test_partial_year_flagged(inputs):
    odd = copy.deepcopy(inputs)
    odd["periods"] = 18
    outputs_odd, _ = evaluate_model(odd)

    _, annual, warnings, _ = compare_outcomes(
        outputs_odd, odd, outputs_odd, odd)

    assert len(annual.period_labels) == 2
    assert any("partial year" in w.lower() for w in warnings)


def test_modified_model_shows_difference(inputs, outputs):
    bigger = copy.deepcopy(inputs)
    bigger["revenue_streams"][0]["price"] = 200.0  # double
    outputs_b, _ = evaluate_model(bigger)

    _, annual, _, _ = compare_outcomes(outputs, inputs, outputs_b, bigger)
    rev = annual.metrics["revenue"]

    assert rev.values_b[0] > rev.values_a[0]
    assert rev.diff[0] > 0
    assert rev.pct_diff[0] is not None and rev.pct_diff[0] > 0


def test_derived_metrics_present(inputs, outputs):
    _, annual, _, _ = compare_outcomes(outputs, inputs, outputs, inputs)
    assert "gross_margin" in annual.metrics
    assert "dscr" in annual.metrics
    gm = annual.metrics["gross_margin"]
    assert gm.values_a[0] is not None and 0 < gm.values_a[0] < 1
