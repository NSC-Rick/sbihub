"""Tests for the model comparison assumption diff engine."""
import copy

from sbi_hub.modules.financial_modeler.comparison.diff import (
    count_by_status,
    diff_model_inputs,
    format_assumption_value,
)
from sbi_hub.modules.financial_modeler.comparison.schema import (
    STATUS_ADDED,
    STATUS_MODIFIED,
    STATUS_REMOVED,
    STATUS_UNCHANGED,
)
from sbi_hub.modules.financial_modeler.engine.validation import (
    get_default_model_inputs,
)


def _by_path(changes):
    return {c.path: c for c in changes}


def test_identical_models_all_unchanged():
    inputs = get_default_model_inputs()
    changes = diff_model_inputs(inputs, copy.deepcopy(inputs))
    assert changes
    assert all(c.status == STATUS_UNCHANGED for c in changes)


def test_scalar_modified_with_abs_and_pct_diff():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["tax_rate"] = 0.30  # from 0.25

    changes = _by_path(diff_model_inputs(a, b))
    change = changes["tax_rate"]

    assert change.status == STATUS_MODIFIED
    assert change.group == "Taxes & Depreciation"
    assert change.value_a == 0.25
    assert change.value_b == 0.30
    assert abs(change.abs_diff - 0.05) < 1e-9
    assert abs(change.pct_diff - 0.20) < 1e-9


def test_scalar_added_and_removed():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["custom_new_field"] = 42
    del b["days_open"]

    changes = _by_path(diff_model_inputs(a, b))
    assert changes["custom_new_field"].status == STATUS_ADDED
    assert changes["custom_new_field"].value_b == 42
    assert changes["days_open"].status == STATUS_REMOVED
    assert changes["days_open"].value_a == 30.0


def test_entity_modified_matched_by_name():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["revenue_streams"][0]["price"] = 150.0

    changes = _by_path(diff_model_inputs(a, b))
    change = changes['revenue_streams["Product Sales"].price']

    assert change.status == STATUS_MODIFIED
    assert change.entity == "Product Sales"
    assert change.group == "Revenue Streams"
    assert "Product Sales" in change.label
    assert change.abs_diff == 50.0


def test_entity_added_and_removed():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["revenue_streams"].append({
        "name": "Catering", "price": 50.0, "volume": 10.0,
        "growth_rate": 0.05, "cogs_override": None,
    })

    changes = _by_path(diff_model_inputs(a, b))
    added = changes['revenue_streams["Catering"]']
    assert added.status == STATUS_ADDED
    assert added.details["price"] == 50.0

    c = copy.deepcopy(a)
    c["revenue_streams"] = []
    changes2 = _by_path(diff_model_inputs(a, c))
    removed = changes2['revenue_streams["Product Sales"]']
    assert removed.status == STATUS_REMOVED
    assert removed.details["name"] == "Product Sales"


def test_renamed_entity_is_remove_plus_add():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["opex_items"][0]["name"] = "Office Rent"  # was "Rent"

    changes = _by_path(diff_model_inputs(a, b))
    assert changes['opex_items["Rent"]'].status == STATUS_REMOVED
    assert changes['opex_items["Office Rent"]'].status == STATUS_ADDED


def test_payroll_roles_match_by_role_key():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["payroll_roles"][0]["headcount"] = 3

    changes = _by_path(diff_model_inputs(a, b))
    change = changes['payroll_roles["Manager"].headcount']
    assert change.status == STATUS_MODIFIED
    assert change.entity == "Manager"
    assert change.abs_diff == 2.0


def test_nested_dict_diff():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["capital_stack"]["uses"]["working_capital"] = 25000.0
    b["owner_compensation"]["amount"] = 60000.0

    changes = _by_path(diff_model_inputs(a, b))
    wc = changes["capital_stack.uses.working_capital"]
    assert wc.status == STATUS_MODIFIED
    assert wc.group == "Capital Structure"
    assert wc.abs_diff == 25000.0

    oc = changes["owner_compensation.amount"]
    assert oc.status == STATUS_MODIFIED
    assert oc.group == "Owner Compensation"


def test_missing_parent_dict_expands_to_leaves():
    a = get_default_model_inputs()
    a["extra_config"] = {"x": 1, "y": 2}
    b = copy.deepcopy(a)
    del b["extra_config"]

    changes = _by_path(diff_model_inputs(a, b))
    assert changes["extra_config.x"].status == STATUS_REMOVED
    assert changes["extra_config.y"].status == STATUS_REMOVED


def test_scalar_list_compared_elementwise():
    a = get_default_model_inputs()
    a["seasonality"]["mode"] = "Custom"
    a["seasonality"]["custom_weights"] = [8.33] * 12
    b = copy.deepcopy(a)
    b["seasonality"]["custom_weights"][0] = 20.0

    changes = _by_path(diff_model_inputs(a, b))
    jan = changes["seasonality.custom_weights[0]"]
    feb = changes["seasonality.custom_weights[1]"]
    assert jan.status == STATUS_MODIFIED
    assert "January" in jan.label
    assert feb.status == STATUS_UNCHANGED


def test_numeric_tolerance_treats_float_noise_as_unchanged():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["tax_rate"] = 0.25 + 1e-12

    changes = _by_path(diff_model_inputs(a, b))
    assert changes["tax_rate"].status == STATUS_UNCHANGED


def test_pct_diff_none_when_base_zero():
    a = get_default_model_inputs()
    a["monthly_revenue"] = 0.0
    b = copy.deepcopy(a)
    b["monthly_revenue"] = 5000.0

    changes = _by_path(diff_model_inputs(a, b))
    change = changes["monthly_revenue"]
    assert change.status == STATUS_MODIFIED
    assert change.abs_diff == 5000.0
    assert change.pct_diff is None


def test_count_by_status():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["tax_rate"] = 0.30
    b["revenue_streams"].append({
        "name": "X", "price": 1.0, "volume": 1.0,
        "growth_rate": 0.0, "cogs_override": None,
    })
    counts = count_by_status(diff_model_inputs(a, b))
    assert counts[STATUS_MODIFIED] == 1
    assert counts[STATUS_ADDED] == 1
    assert counts[STATUS_REMOVED] == 0
    assert counts[STATUS_UNCHANGED] > 0


def test_deterministic_order():
    a = get_default_model_inputs()
    b = copy.deepcopy(a)
    b["tax_rate"] = 0.30
    first = diff_model_inputs(a, b)
    second = diff_model_inputs(a, b)
    assert [c.path for c in first] == [c.path for c in second]


def test_format_assumption_value():
    assert format_assumption_value(0.06, "", "loan_annual_rate") == "6.00%"
    assert format_assumption_value(60000.0, "", "loan_principal") == "$60,000.00"
    assert format_assumption_value(30, "", "ar_days") == "30"
    assert format_assumption_value(0.5, "payroll_roles[0].rate", "rate") == "$0.50"
    assert format_assumption_value(0.06, "capital_stack.sources.bank_loan.rate", "rate") == "6.00%"
    assert format_assumption_value(None) == "—"
    assert format_assumption_value(True) == "Yes"
    assert format_assumption_value("salary") == "salary"
