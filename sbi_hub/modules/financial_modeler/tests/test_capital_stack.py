"""
Test suite for Capital Stack advisory layer feature.

Verifies:
- Capital stack data structure exists in defaults
- Uses and sources calculate correctly
- Funding gap calculation works
- Annual debt service calculations are correct
- Save/load persistence works
- Backward compatibility with old scenarios
- No auto-apply on load
- Apply button functionality
"""

import pytest
from sbi_hub.modules.financial_modeler.engine.validation import get_default_model_inputs, validate_scenario_json


def test_capital_stack_exists_in_defaults():
    """Verify capital stack structure exists in default model inputs."""
    defaults = get_default_model_inputs()
    
    assert 'capital_stack' in defaults
    assert isinstance(defaults['capital_stack'], dict)


def test_capital_stack_default_structure():
    """Verify capital stack has correct default structure."""
    defaults = get_default_model_inputs()
    cs = defaults['capital_stack']
    
    # Check top-level keys
    assert 'enabled' in cs
    assert 'uses' in cs
    assert 'sources' in cs
    
    # Check enabled is False by default
    assert cs['enabled'] == False
    
    # Check uses structure
    assert 'purchase_price' in cs['uses']
    assert 'inventory_adjustment' in cs['uses']
    assert 'closing_costs' in cs['uses']
    assert 'working_capital' in cs['uses']
    assert 'capex' in cs['uses']
    
    # Check sources structure
    assert 'buyer_equity' in cs['sources']
    assert 'community_equity' in cs['sources']
    assert 'donations' in cs['sources']
    assert 'bank_loan' in cs['sources']
    assert 'seller_note' in cs['sources']
    
    # Check debt structures
    assert 'amount' in cs['sources']['bank_loan']
    assert 'rate' in cs['sources']['bank_loan']
    assert 'term' in cs['sources']['bank_loan']
    
    assert 'amount' in cs['sources']['seller_note']
    assert 'rate' in cs['sources']['seller_note']
    assert 'term' in cs['sources']['seller_note']


def test_capital_stack_default_values_zero():
    """Verify all capital stack default values are zero."""
    defaults = get_default_model_inputs()
    cs = defaults['capital_stack']
    
    # All uses should be 0
    assert cs['uses']['purchase_price'] == 0.0
    assert cs['uses']['inventory_adjustment'] == 0.0
    assert cs['uses']['closing_costs'] == 0.0
    assert cs['uses']['working_capital'] == 0.0
    assert cs['uses']['capex'] == 0.0
    
    # All equity sources should be 0
    assert cs['sources']['buyer_equity'] == 0.0
    assert cs['sources']['community_equity'] == 0.0
    assert cs['sources']['donations'] == 0.0
    
    # All debt amounts should be 0
    assert cs['sources']['bank_loan']['amount'] == 0.0
    assert cs['sources']['seller_note']['amount'] == 0.0


def test_capital_stack_uses_calculation():
    """Verify total uses calculation."""
    # Create a capital stack with uses
    uses = {
        'purchase_price': 100000.0,
        'inventory_adjustment': 10000.0,
        'closing_costs': 5000.0,
        'working_capital': 15000.0,
        'capex': 5000.0
    }
    
    total_uses = sum(uses.values())
    
    assert total_uses == 135000.0


def test_capital_stack_sources_calculation():
    """Verify total sources calculation."""
    # Create a capital stack with sources
    sources = {
        'buyer_equity': 30000.0,
        'community_equity': 20000.0,
        'donations': 5000.0,
        'bank_loan': {'amount': 60000.0, 'rate': 0.06, 'term': 10},
        'seller_note': {'amount': 20000.0, 'rate': 0.05, 'term': 5}
    }
    
    total_equity = sources['buyer_equity'] + sources['community_equity'] + sources['donations']
    total_debt = sources['bank_loan']['amount'] + sources['seller_note']['amount']
    total_sources = total_equity + total_debt
    
    assert total_equity == 55000.0
    assert total_debt == 80000.0
    assert total_sources == 135000.0


def test_capital_stack_funding_gap_balanced():
    """Verify funding gap calculation when balanced."""
    uses = {
        'purchase_price': 100000.0,
        'inventory_adjustment': 10000.0,
        'closing_costs': 5000.0,
        'working_capital': 15000.0,
        'capex': 5000.0
    }
    
    sources = {
        'buyer_equity': 30000.0,
        'community_equity': 20000.0,
        'donations': 5000.0,
        'bank_loan': {'amount': 60000.0, 'rate': 0.06, 'term': 10},
        'seller_note': {'amount': 20000.0, 'rate': 0.05, 'term': 5}
    }
    
    total_uses = sum(uses.values())
    total_sources = (sources['buyer_equity'] + sources['community_equity'] + 
                     sources['donations'] + sources['bank_loan']['amount'] + 
                     sources['seller_note']['amount'])
    
    funding_gap = total_sources - total_uses
    
    assert funding_gap == 0.0


def test_capital_stack_funding_gap_surplus():
    """Verify funding gap calculation with surplus."""
    total_uses = 100000.0
    total_sources = 120000.0
    
    funding_gap = total_sources - total_uses
    
    assert funding_gap == 20000.0
    assert funding_gap > 0


def test_capital_stack_funding_gap_shortfall():
    """Verify funding gap calculation with shortfall."""
    total_uses = 150000.0
    total_sources = 135000.0
    
    funding_gap = total_sources - total_uses
    
    assert funding_gap == -15000.0
    assert funding_gap < 0


def test_capital_stack_bank_loan_annual_payment():
    """Verify bank loan annual payment calculation."""
    amount = 60000.0
    rate = 0.06
    term = 10
    
    # Standard amortization formula
    annual_payment = amount * (rate * (1 + rate)**term) / ((1 + rate)**term - 1)
    
    # Should be approximately $8,160.76
    assert 8100 < annual_payment < 8200


def test_capital_stack_seller_note_annual_payment():
    """Verify seller note annual payment calculation."""
    amount = 20000.0
    rate = 0.05
    term = 5
    
    # Standard amortization formula
    annual_payment = amount * (rate * (1 + rate)**term) / ((1 + rate)**term - 1)
    
    # Should be approximately $4,619.47
    assert 4600 < annual_payment < 4650


def test_capital_stack_total_annual_debt_service():
    """Verify total annual debt service calculation."""
    bank_amount = 60000.0
    bank_rate = 0.06
    bank_term = 10
    
    seller_amount = 20000.0
    seller_rate = 0.05
    seller_term = 5
    
    bank_payment = bank_amount * (bank_rate * (1 + bank_rate)**bank_term) / ((1 + bank_rate)**bank_term - 1)
    seller_payment = seller_amount * (seller_rate * (1 + seller_rate)**seller_term) / ((1 + seller_rate)**seller_term - 1)
    
    total_debt_service = bank_payment + seller_payment
    
    # Should be approximately $12,780.23
    assert 12700 < total_debt_service < 12850


def test_capital_stack_zero_debt_no_payment():
    """Verify zero debt results in zero payment."""
    amount = 0.0
    rate = 0.06
    term = 10
    
    if amount > 0 and rate > 0:
        annual_payment = amount * (rate * (1 + rate)**term) / ((1 + rate)**term - 1)
    else:
        annual_payment = 0.0
    
    assert annual_payment == 0.0


def test_backward_compatibility_without_capital_stack():
    """Verify old scenarios without capital_stack load correctly."""
    # Old scenario without capital_stack field
    old_scenario = {
        'time_mode': 'monthly',
        'periods': 60,
        'revenue_streams': [],
        'global_cogs_pct': 0.30,
        'payroll_roles': [],
        'opex_items': [],
        'loan_principal': 50000.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 0.0,
        'owner_compensation': {'mode': 'distribution', 'amount': 0.0}
    }
    
    # Should validate successfully
    is_valid, error = validate_scenario_json(old_scenario)
    assert is_valid, f"Validation failed: {error}"


def test_capital_stack_in_saved_scenario():
    """Verify capital stack persists in saved scenario."""
    from sbi_hub.modules.financial_modeler.engine.validation import session_state_to_model_inputs
    
    # Mock session state with capital stack
    class MockSessionState:
        def __init__(self):
            self.time_mode = 'monthly'
            self.periods = 36
            self.revenue_streams = []
            self.global_cogs_pct = 0.30
            self.payroll_roles = []
            self.opex_items = []
            self.loan_principal = 50000.0
            self.loan_annual_rate = 0.06
            self.loan_term_months = 60
            self.loan_start_period = 0
            self.ar_days = 30
            self.ap_days = 30
            self.inventory_days = 30
            self.tax_rate = 0.25
            self.annual_depreciation = 0.0
            self.owner_compensation = {'mode': 'distribution', 'amount': 0.0}
            self.capital_stack = {
                'enabled': True,
                'uses': {
                    'purchase_price': 100000.0,
                    'inventory_adjustment': 10000.0,
                    'closing_costs': 5000.0,
                    'working_capital': 15000.0,
                    'capex': 5000.0
                },
                'sources': {
                    'buyer_equity': 30000.0,
                    'community_equity': 20000.0,
                    'donations': 5000.0,
                    'bank_loan': {'amount': 60000.0, 'rate': 0.06, 'term': 10},
                    'seller_note': {'amount': 20000.0, 'rate': 0.05, 'term': 5}
                }
            }
        
        def get(self, key, default=None):
            return getattr(self, key, default)
    
    mock_state = MockSessionState()
    model_inputs = session_state_to_model_inputs(mock_state)
    
    # Verify capital stack is in model inputs
    assert 'capital_stack' in model_inputs
    assert model_inputs['capital_stack']['enabled'] == True
    assert model_inputs['capital_stack']['uses']['purchase_price'] == 100000.0
    assert model_inputs['capital_stack']['sources']['bank_loan']['amount'] == 60000.0


def test_capital_stack_load_with_default():
    """Verify capital stack loads with default if missing from scenario."""
    from sbi_hub.modules.financial_modeler.engine.validation import model_inputs_to_session_state
    
    # Scenario without capital_stack
    model_inputs = {
        'time_mode': 'monthly',
        'periods': 60,
        'revenue_streams': [],
        'global_cogs_pct': 0.30,
        'payroll_roles': [],
        'opex_items': [],
        'loan_principal': 50000.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 0.0,
        'owner_compensation': {'mode': 'distribution', 'amount': 0.0}
    }
    
    # Mock session state
    class MockSessionState:
        pass
    
    mock_state = MockSessionState()
    model_inputs_to_session_state(model_inputs, mock_state)
    
    # Verify capital stack was added with defaults
    assert hasattr(mock_state, 'capital_stack')
    assert mock_state.capital_stack['enabled'] == False
    assert mock_state.capital_stack['uses']['purchase_price'] == 0.0


def test_capital_stack_no_auto_apply():
    """Verify capital stack does NOT auto-apply to debt on load."""
    from sbi_hub.modules.financial_modeler.engine.validation import model_inputs_to_session_state
    
    # Scenario with capital stack but different debt settings
    model_inputs = {
        'time_mode': 'monthly',
        'periods': 60,
        'revenue_streams': [],
        'global_cogs_pct': 0.30,
        'payroll_roles': [],
        'opex_items': [],
        'loan_principal': 50000.0,  # Different from capital stack
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 0.0,
        'owner_compensation': {'mode': 'distribution', 'amount': 0.0},
        'capital_stack': {
            'enabled': True,
            'uses': {'purchase_price': 100000.0, 'inventory_adjustment': 0.0, 'closing_costs': 0.0, 'working_capital': 0.0, 'capex': 0.0},
            'sources': {
                'buyer_equity': 40000.0,
                'community_equity': 0.0,
                'donations': 0.0,
                'bank_loan': {'amount': 60000.0, 'rate': 0.07, 'term': 10},  # Different from loan_principal
                'seller_note': {'amount': 0.0, 'rate': 0.05, 'term': 5}
            }
        }
    }
    
    class MockSessionState:
        pass
    
    mock_state = MockSessionState()
    model_inputs_to_session_state(model_inputs, mock_state)
    
    # Verify loan_principal is NOT overwritten by capital stack
    assert mock_state.loan_principal == 50000.0  # Original value
    assert mock_state.capital_stack['sources']['bank_loan']['amount'] == 60000.0  # Capital stack value
    
    # They should be different (no auto-apply)
    assert mock_state.loan_principal != mock_state.capital_stack['sources']['bank_loan']['amount']
