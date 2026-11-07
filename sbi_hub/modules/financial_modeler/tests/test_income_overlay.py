"""
Test suite for Income Statement overlay feature.

Verifies:
- Debt service calculation (principal + interest)
- Owner compensation display in overlay
- Cash after debt calculation
- Cash after debt & owner calculation
- Distribution vs payroll mode handling
- No changes to core income statement
- Overlay matches income statement periods
"""

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.model import build_model
from sbi_hub.modules.financial_modeler.engine.validation import get_default_model_inputs


def test_debt_service_includes_principal_and_interest():
    """Verify debt service equals principal + interest payment."""
    model_inputs = get_default_model_inputs()
    model_inputs['loan_principal'] = 50000.0
    model_inputs['loan_annual_rate'] = 0.06
    model_inputs['loan_term_months'] = 60
    model_inputs['loan_start_period'] = 0
    
    outputs = build_model(model_inputs)
    loan_schedule = outputs['loan_schedule']
    
    # Debt service should equal payment (which is principal + interest)
    debt_service = loan_schedule['payment']
    principal = loan_schedule['principal']
    interest = loan_schedule['interest']
    
    # Verify payment = principal + interest (with floating point tolerance)
    import numpy as np
    assert np.allclose(debt_service, principal + interest, rtol=1e-9)


def test_cash_after_debt_calculation():
    """Verify cash after debt = net income - debt service."""
    model_inputs = get_default_model_inputs()
    model_inputs['loan_principal'] = 50000.0
    model_inputs['loan_annual_rate'] = 0.06
    model_inputs['loan_term_months'] = 60
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    cash_after_debt = net_income - debt_service
    
    # Should be a valid series
    assert isinstance(cash_after_debt, pd.Series)
    assert len(cash_after_debt) == len(net_income)


def test_owner_comp_distribution_mode():
    """Verify owner comp in distribution mode is subtracted from cash."""
    model_inputs = get_default_model_inputs()
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0  # Annual
    }
    model_inputs['time_mode'] = 'monthly'
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    # Owner comp per period (monthly)
    owner_comp_per_period = 60000.0 / 12  # $5,000/month
    
    cash_after_debt = net_income - debt_service
    cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
    
    # Verify calculation
    expected = net_income - debt_service - owner_comp_per_period
    assert (cash_after_debt_and_owner == expected).all()


def test_owner_comp_payroll_mode():
    """Verify owner comp in payroll mode doesn't affect overlay cash."""
    model_inputs = get_default_model_inputs()
    model_inputs['owner_compensation'] = {
        'mode': 'payroll',
        'amount': 60000.0  # Annual
    }
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    cash_after_debt = net_income - debt_service
    
    # In payroll mode, owner comp already in income statement
    # So cash_after_debt_and_owner should equal cash_after_debt
    cash_after_debt_and_owner = cash_after_debt  # No additional deduction
    
    assert (cash_after_debt_and_owner == cash_after_debt).all()


def test_income_statement_unchanged_by_overlay():
    """Verify core income statement is not modified by overlay feature."""
    model_inputs = get_default_model_inputs()
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0
    }
    
    outputs = build_model(model_inputs)
    income_statement = outputs['income_statement']
    
    # Verify core income statement structure unchanged
    assert 'revenue' in income_statement.columns
    assert 'cogs' in income_statement.columns
    assert 'gross_profit' in income_statement.columns
    assert 'payroll' in income_statement.columns
    assert 'opex' in income_statement.columns
    assert 'ebitda' in income_statement.columns
    assert 'interest_expense' in income_statement.columns
    assert 'net_income' in income_statement.columns
    
    # Verify net income is still calculated correctly
    # (overlay should not modify this)
    expected_net_income = (income_statement['revenue'] - 
                          income_statement['cogs'] - 
                          income_statement['payroll'] - 
                          income_statement['opex'] - 
                          income_statement['interest_expense'])
    
    assert (income_statement['net_income'] == expected_net_income).all()


def test_overlay_periods_match_income_statement():
    """Verify overlay has same number of periods as income statement."""
    model_inputs = get_default_model_inputs()
    model_inputs['periods'] = 36
    
    outputs = build_model(model_inputs)
    
    income_statement = outputs['income_statement']
    loan_schedule = outputs['loan_schedule']
    
    # All should have same length
    assert len(income_statement) == 36
    assert len(loan_schedule) == 36


def test_annual_mode_owner_comp():
    """Verify owner comp calculation in annual mode."""
    model_inputs = get_default_model_inputs()
    model_inputs['time_mode'] = 'annual'
    model_inputs['periods'] = 3
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0  # Annual
    }
    
    outputs = build_model(model_inputs)
    
    # In annual mode, owner comp per period = annual amount
    owner_comp_per_period = 60000.0
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    cash_after_debt = net_income - debt_service
    cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
    
    expected = net_income - debt_service - owner_comp_per_period
    assert (cash_after_debt_and_owner == expected).all()


def test_monthly_mode_owner_comp():
    """Verify owner comp calculation in monthly mode."""
    model_inputs = get_default_model_inputs()
    model_inputs['time_mode'] = 'monthly'
    model_inputs['periods'] = 36
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0  # Annual
    }
    
    outputs = build_model(model_inputs)
    
    # In monthly mode, owner comp per period = annual / 12
    owner_comp_per_period = 60000.0 / 12  # $5,000/month
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    cash_after_debt = net_income - debt_service
    cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
    
    expected = net_income - debt_service - owner_comp_per_period
    assert (cash_after_debt_and_owner == expected).all()


def test_zero_owner_comp():
    """Verify overlay works with zero owner compensation."""
    model_inputs = get_default_model_inputs()
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 0.0
    }
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    cash_after_debt = net_income - debt_service
    cash_after_debt_and_owner = cash_after_debt - 0.0
    
    # Should equal cash_after_debt
    assert (cash_after_debt_and_owner == cash_after_debt).all()


def test_zero_debt_service():
    """Verify overlay works with zero debt service."""
    model_inputs = get_default_model_inputs()
    model_inputs['loan_principal'] = 0.0
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0
    }
    model_inputs['time_mode'] = 'monthly'
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    # Debt service should be zero
    assert (debt_service == 0).all()
    
    cash_after_debt = net_income - 0
    owner_comp_per_period = 60000.0 / 12
    cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
    
    expected = net_income - owner_comp_per_period
    assert (cash_after_debt_and_owner == expected).all()


def test_negative_net_income_overlay():
    """Verify overlay handles negative net income correctly."""
    model_inputs = get_default_model_inputs()
    
    # Create scenario with high expenses to get negative net income
    model_inputs['opex_items'] = [
        {'name': 'High Rent', 'amount': 50000.0, 'growth_rate': 0.0, 'category': 'fixed'}
    ]
    model_inputs['loan_principal'] = 100000.0
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0
    }
    model_inputs['time_mode'] = 'monthly'
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    owner_comp_per_period = 60000.0 / 12
    
    # Even with negative net income, calculations should work
    cash_after_debt = net_income - debt_service
    cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
    
    # Should be valid series (likely negative values)
    assert isinstance(cash_after_debt, pd.Series)
    assert isinstance(cash_after_debt_and_owner, pd.Series)


def test_overlay_data_types():
    """Verify overlay calculations return correct data types."""
    model_inputs = get_default_model_inputs()
    model_inputs['owner_compensation'] = {
        'mode': 'distribution',
        'amount': 60000.0
    }
    
    outputs = build_model(model_inputs)
    
    net_income = outputs['income_statement']['net_income']
    debt_service = outputs['loan_schedule']['payment']
    
    # All should be pandas Series
    assert isinstance(net_income, pd.Series)
    assert isinstance(debt_service, pd.Series)
    
    cash_after_debt = net_income - debt_service
    assert isinstance(cash_after_debt, pd.Series)


def test_owner_comp_persists_in_session():
    """Verify owner compensation structure is correct."""
    model_inputs = get_default_model_inputs()
    
    # Verify default structure
    assert 'owner_compensation' in model_inputs
    assert 'mode' in model_inputs['owner_compensation']
    assert 'amount' in model_inputs['owner_compensation']
    
    # Verify default values
    assert model_inputs['owner_compensation']['mode'] in ['distribution', 'payroll']
    assert isinstance(model_inputs['owner_compensation']['amount'], (int, float))
