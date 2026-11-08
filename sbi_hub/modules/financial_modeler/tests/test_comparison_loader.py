"""Tests for comparison model loading (file parsing + session snapshot)."""
import json

from sbi_hub.modules.financial_modeler.comparison.loader import (
    parse_model_file,
    snapshot_current_model,
)
from sbi_hub.modules.financial_modeler.engine.validation import (
    get_default_model_inputs,
)


class MockSessionState:
    """Minimal session-state stand-in (same pattern as test_scenario_json)."""

    def __init__(self):
        self.time_mode = "monthly"
        self.periods = 36
        self.revenue_streams = []
        self.global_cogs_pct = 0.30
        self.payroll_roles = []
        self.opex_items = []
        self.loan_principal = 0.0
        self.loan_annual_rate = 0.0
        self.loan_term_months = 60
        self.loan_start_period = 0
        self.ar_days = 30
        self.ap_days = 30
        self.inventory_days = 30
        self.tax_rate = 0.25
        self.annual_depreciation = 0.0
        self.scenario_name = "Test Biz"
        self.business_stage = "existing"
        self.model_mode = "acquisition"
        self.working_capital_source = "buyer_injected"

    def get(self, key, default=None):
        return getattr(self, key, default)


def test_parse_valid_model_file():
    data = json.dumps(get_default_model_inputs()).encode("utf-8")
    inputs, errors = parse_model_file(data, "model.json")
    assert errors == []
    assert inputs["time_mode"] == "monthly"


def test_parse_rejects_invalid_json():
    inputs, errors = parse_model_file(b"{not json", "bad.json")
    assert inputs is None
    assert len(errors) == 1
    assert "bad.json" in errors[0]


def test_parse_rejects_non_dict_json():
    inputs, errors = parse_model_file(b"[1, 2, 3]", "list.json")
    assert inputs is None
    assert errors


def test_parse_rejects_incompatible_model():
    inputs, errors = parse_model_file(b'{"foo": 1}', "other.json")
    assert inputs is None
    assert errors
    assert "not a compatible model file" in errors[0]


def test_parse_rejects_non_utf8():
    inputs, errors = parse_model_file(b"\xff\xfe\x00\x01", "binary.bin")
    assert inputs is None
    assert errors


def test_parse_accepts_str_input():
    inputs, errors = parse_model_file(
        json.dumps(get_default_model_inputs()), "model.json")
    assert errors == []
    assert inputs is not None


def test_snapshot_includes_session_only_keys():
    session = MockSessionState()
    snap = snapshot_current_model(session)
    assert snap["business_stage"] == "existing"
    assert snap["model_mode"] == "acquisition"
    assert snap["working_capital_source"] == "buyer_injected"
    assert snap["scenario_name"] == "Test Biz"
    assert "platform_version" in snap


def test_snapshot_does_not_mutate_session():
    session = MockSessionState()
    session.revenue_streams = [{"name": "S", "price": 1.0, "volume": 1.0,
                                "growth_rate": 0.0, "cogs_override": None}]
    snap = snapshot_current_model(session)
    snap["revenue_streams"][0]["price"] = 999.0
    snap["tax_rate"] = 0.99
    assert session.revenue_streams[0]["price"] == 1.0
    assert session.tax_rate == 0.25
