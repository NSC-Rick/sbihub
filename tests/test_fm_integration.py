"""Integration smoke tests for the vendored Financial Modeler module.

Verifies the engine is importable through the sbi_hub package namespace and
produces expected outputs for a synthetic scenario. Detailed calculation
coverage lives in the module's own test suite under
``sbi_hub/modules/financial_modeler/tests``.
"""
import json

import pytest


def test_engine_importable_via_package():
    from sbi_hub.modules.financial_modeler.engine.model import build_model
    assert callable(build_model)


def test_synthetic_scenario_builds():
    from sbi_hub.modules.financial_modeler.engine.model import build_model

    inputs = {
        "time_mode": "monthly",
        "periods": 36,
        "revenue_streams": [
            {"name": "Synthetic Sales", "price": 100.0, "volume": 100.0,
             "growth_rate": 0.10, "cogs_override": None}
        ],
        "global_cogs_pct": 0.30,
        "payroll_roles": [
            {"role": "Manager", "headcount": 1, "pay_type": "salary",
             "rate": 60000.0, "hours_per_week": 40, "annual_raise_pct": 0.03,
             "payroll_tax_pct": 0.0765, "benefits_pct": 0.15}
        ],
        "opex_items": [{"name": "Rent", "amount": 2000.0, "growth_rate": 0.03}],
        "loan_principal": 50000.0,
        "loan_annual_rate": 0.06,
        "loan_term_months": 60,
        "loan_start_period": 0,
        "ar_days": 30,
        "ap_days": 30,
        "inventory_days": 30,
    }
    outputs = build_model(inputs)

    assert len(outputs["pnl_statement"]) == 36
    assert len(outputs["income_statement"]) == 36
    assert len(outputs["cash_flow_statement"]) == 36
    assert len(outputs["kpis"]) == 36


def test_module_entry_point_exposes_render():
    pytest.importorskip("streamlit")
    from sbi_hub.modules.financial_modeler import app as fm_app
    assert callable(fm_app.render)


def test_scenario_json_roundtrip(tmp_path):
    """Saved-scenario compatibility: a serialized scenario re-validates cleanly."""
    from sbi_hub.modules.financial_modeler.engine.validation import (
        get_default_model_inputs,
        validate_scenario_json,
    )

    scenario = get_default_model_inputs()
    scenario["scenario_name"] = "Synthetic Co"

    path = tmp_path / "synthetic_scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")

    loaded = json.loads(path.read_text(encoding="utf-8"))
    ok, message = validate_scenario_json(loaded)
    assert ok, f"scenario failed validation: {message}"
