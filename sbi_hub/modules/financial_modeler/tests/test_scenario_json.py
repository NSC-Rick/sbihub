import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from sbi_hub.modules.financial_modeler.engine.validation import (
    get_default_model_inputs,
    validate_scenario_json,
    session_state_to_model_inputs,
    model_inputs_to_session_state
)


class MockSessionState:
    """Mock Streamlit session state for testing."""
    def __init__(self):
        self.time_mode = 'monthly'
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
    
    def get(self, key, default=None):
        return getattr(self, key, default)


def test_json_roundtrip():
    """Test that model inputs can be saved and loaded without data loss."""
    defaults = get_default_model_inputs()
    
    json_str = json.dumps(defaults, indent=2)
    
    loaded = json.loads(json_str)
    
    assert defaults == loaded


def test_validate_valid_scenario():
    """Test validation passes for valid scenario."""
    defaults = get_default_model_inputs()
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert is_valid
    assert error_msg == ""


def test_validate_missing_keys():
    """Test validation fails for missing required keys."""
    incomplete = {
        'time_mode': 'monthly',
        'periods': 60
    }
    
    is_valid, error_msg = validate_scenario_json(incomplete)
    
    assert not is_valid
    assert "Missing required keys" in error_msg


def test_validate_invalid_time_mode():
    """Test validation fails for invalid time mode."""
    defaults = get_default_model_inputs()
    defaults['time_mode'] = 'invalid'
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "time_mode must be" in error_msg


def test_validate_non_dict():
    """Test validation fails for non-dictionary input."""
    is_valid, error_msg = validate_scenario_json("not a dict")
    
    assert not is_valid
    assert "must be a JSON object" in error_msg


def test_validate_invalid_revenue_streams():
    """Test validation fails for invalid revenue streams."""
    defaults = get_default_model_inputs()
    defaults['revenue_streams'] = "not a list"
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "revenue_streams must be a list" in error_msg


def test_validate_missing_revenue_stream_keys():
    """Test validation fails for revenue stream missing keys."""
    defaults = get_default_model_inputs()
    defaults['revenue_streams'] = [{'name': 'Test'}]
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "revenue_streams[0] missing keys" in error_msg


def test_validate_invalid_payroll_roles():
    """Test validation fails for invalid payroll roles."""
    defaults = get_default_model_inputs()
    defaults['payroll_roles'] = "not a list"
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "payroll_roles must be a list" in error_msg


def test_validate_missing_payroll_role_keys():
    """Test validation fails for payroll role missing keys."""
    defaults = get_default_model_inputs()
    defaults['payroll_roles'] = [{'role': 'Test'}]
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "payroll_roles[0] missing keys" in error_msg


def test_validate_invalid_opex_items():
    """Test validation fails for invalid opex items."""
    defaults = get_default_model_inputs()
    defaults['opex_items'] = "not a list"
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "opex_items must be a list" in error_msg


def test_validate_missing_opex_item_keys():
    """Test validation fails for opex item missing keys."""
    defaults = get_default_model_inputs()
    defaults['opex_items'] = [{'name': 'Test'}]
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert not is_valid
    assert "opex_items[0] missing keys" in error_msg


def test_session_state_to_model_inputs():
    """Test conversion from session state to model inputs."""
    session = MockSessionState()
    session.time_mode = 'annual'
    session.periods = 5
    session.revenue_streams = [{'name': 'Test', 'price': 100, 'volume': 50, 'growth_rate': 0.1, 'cogs_override': None}]
    session.tax_rate = 0.30
    
    model_inputs = session_state_to_model_inputs(session)
    
    assert model_inputs['time_mode'] == 'annual'
    assert model_inputs['periods'] == 5
    assert model_inputs['tax_rate'] == 0.30
    assert len(model_inputs['revenue_streams']) == 1


def test_model_inputs_to_session_state():
    """Test loading model inputs into session state."""
    session = MockSessionState()
    
    model_inputs = {
        'time_mode': 'annual',
        'periods': 5,
        'revenue_streams': [{'name': 'Test', 'price': 100, 'volume': 50, 'growth_rate': 0.1, 'cogs_override': None}],
        'global_cogs_pct': 0.35,
        'payroll_roles': [],
        'opex_items': [],
        'loan_principal': 100000.0,
        'loan_annual_rate': 0.08,
        'loan_term_months': 120,
        'loan_start_period': 1,
        'ar_days': 45,
        'ap_days': 60,
        'inventory_days': 90,
        'tax_rate': 0.30,
        'annual_depreciation': 10000.0
    }
    
    model_inputs_to_session_state(model_inputs, session)
    
    assert session.time_mode == 'annual'
    assert session.periods == 5
    assert session.global_cogs_pct == 0.35
    assert session.loan_principal == 100000.0
    assert session.tax_rate == 0.30
    assert session.annual_depreciation == 10000.0


def test_roundtrip_with_session_state():
    """Test complete roundtrip: session state -> model inputs -> JSON -> model inputs -> session state."""
    session1 = MockSessionState()
    session1.time_mode = 'monthly'
    session1.periods = 36
    session1.revenue_streams = [
        {
            'name': 'Product A',
            'price': 150.0,
            'volume': 200.0,
            'growth_rate': 0.15,
            'cogs_override': 0.25
        }
    ]
    session1.tax_rate = 0.28
    session1.annual_depreciation = 8000.0
    
    model_inputs1 = session_state_to_model_inputs(session1)
    
    json_str = json.dumps(model_inputs1, indent=2)
    
    model_inputs2 = json.loads(json_str)
    
    is_valid, _ = validate_scenario_json(model_inputs2)
    assert is_valid
    
    session2 = MockSessionState()
    model_inputs_to_session_state(model_inputs2, session2)
    
    assert session2.time_mode == session1.time_mode
    assert session2.periods == session1.periods
    assert session2.tax_rate == session1.tax_rate
    assert session2.annual_depreciation == session1.annual_depreciation
    assert len(session2.revenue_streams) == len(session1.revenue_streams)
    assert session2.revenue_streams[0]['name'] == session1.revenue_streams[0]['name']


def test_validate_extra_keys_ignored():
    """Test that extra keys in JSON are ignored (forward compatibility)."""
    defaults = get_default_model_inputs()
    defaults['extra_key'] = 'should be ignored'
    defaults['future_feature'] = 123
    
    is_valid, error_msg = validate_scenario_json(defaults)
    
    assert is_valid
    assert error_msg == ""


def test_get_default_model_inputs_structure():
    """Test that default model inputs have correct structure."""
    defaults = get_default_model_inputs()
    
    assert 'time_mode' in defaults
    assert 'periods' in defaults
    assert 'revenue_streams' in defaults
    assert 'payroll_roles' in defaults
    assert 'opex_items' in defaults
    assert 'tax_rate' in defaults
    assert 'annual_depreciation' in defaults
    
    assert defaults['time_mode'] == 'monthly'
    assert defaults['periods'] == 36
    assert isinstance(defaults['revenue_streams'], list)
    assert isinstance(defaults['payroll_roles'], list)
    assert isinstance(defaults['opex_items'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
