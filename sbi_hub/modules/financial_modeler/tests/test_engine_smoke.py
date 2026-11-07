import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.model import build_model


def get_default_inputs(time_mode='monthly'):
    """Get default model inputs for testing."""
    periods = 36 if time_mode == 'monthly' else 3
    
    return {
        'time_mode': time_mode,
        'periods': periods,
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 100.0,
                'volume': 100.0,
                'growth_rate': 0.10,
                'cogs_override': None
            }
        ],
        'global_cogs_pct': 0.30,
        'payroll_roles': [
            {
                'role': 'Manager',
                'headcount': 1,
                'pay_type': 'salary',
                'rate': 60000.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15
            }
        ],
        'opex_items': [
            {
                'name': 'Rent',
                'amount': 2000.0,
                'growth_rate': 0.03
            }
        ],
        'loan_principal': 50000.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30
    }


def test_model_builds_monthly():
    """Test that model builds successfully in monthly mode."""
    inputs = get_default_inputs('monthly')
    outputs = build_model(inputs)
    
    assert len(outputs['pnl_statement']) == 36  
    assert 'income_statement' in outputs
    assert 'cash_flow_statement' in outputs
    assert 'kpis' in outputs
    
    assert len(outputs['income_statement']) == 36
    assert len(outputs['cash_flow_statement']) == 36
    assert len(outputs['kpis']) == 36


def test_model_builds_annual():
    """Test that model builds successfully in annual mode."""
    inputs = get_default_inputs('annual')
    outputs = build_model(inputs)
    
    assert len(outputs['pnl_statement']) == 3  
    assert 'income_statement' in outputs
    assert 'cash_flow_statement' in outputs
    assert 'kpis' in outputs
    
    assert len(outputs['income_statement']) == 3
    assert len(outputs['cash_flow_statement']) == 3
    assert len(outputs['kpis']) == 3


def test_revenue_output_shape():
    """Test that revenue output has correct shape."""
    inputs = get_default_inputs('monthly')
    outputs = build_model(inputs)
    
    revenue_df = outputs['revenue_df']
    
    assert len(outputs['pnl_statement']) == 36   
    assert 'total' in revenue_df.columns
    assert 'Product Sales' in revenue_df.columns
    assert len(revenue_df) == 36


def test_multiple_revenue_streams():
    """Test model with multiple revenue streams."""
    inputs = get_default_inputs('monthly')
    inputs['revenue_streams'].append({
        'name': 'Service Revenue',
        'price': 200.0,
        'volume': 50.0,
        'growth_rate': 0.05,
        'cogs_override': 0.20
    })
    
    outputs = build_model(inputs)
    revenue_df = outputs['revenue_df']
    
    assert 'Product Sales' in revenue_df.columns
    assert 'Service Revenue' in revenue_df.columns
    assert 'total' in revenue_df.columns


def test_income_statement_structure():
    """Test income statement has required columns."""
    inputs = get_default_inputs('monthly')
    outputs = build_model(inputs)
    
    income_statement = outputs['income_statement']
    
    required_columns = [
        'revenue', 'cogs', 'gross_profit', 'payroll', 'opex',
        'operating_expenses', 'ebitda', 'interest_expense', 'net_income'
    ]
    
    for col in required_columns:
        assert col in income_statement.columns


def test_cash_flow_statement_structure():
    """Test cash flow statement has required columns."""
    inputs = get_default_inputs('monthly')
    outputs = build_model(inputs)
    
    cash_flow = outputs['cash_flow_statement']
    
    required_columns = [
        'net_income', 'ar_change', 'ap_change', 'inventory_change',
        'operating_cash_flow', 'financing_cash_flow', 'net_cash_flow', 'ending_cash'
    ]
    
    for col in required_columns:
        assert col in cash_flow.columns


def test_kpis_structure():
    """Test KPIs have required columns."""
    inputs = get_default_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    
    required_columns = ['ebitda', 'debt_service', 'dscr', 'ending_cash']
    
    for col in required_columns:
        assert col in kpis.columns


def test_no_revenue_streams():
    """Test model with no revenue streams."""
    inputs = get_default_inputs('monthly')
    inputs['revenue_streams'] = []
    
    outputs = build_model(inputs)
    
    assert len(outputs['pnl_statement']) == 36
    assert outputs['revenue_df']['total'].sum() == 0


def test_no_payroll_roles():
    """Test model with no payroll roles."""
    inputs = get_default_inputs('monthly')
    inputs['payroll_roles'] = []
    
    outputs = build_model(inputs)
    
    assert len(outputs['pnl_statement']) == 36
    assert outputs['payroll_df']['total'].sum() == 0


def test_no_loan():
    """Test model handles zero loan principal."""
    inputs = get_default_inputs('monthly')
    inputs['loan_principal'] = 0
    
    outputs = build_model(inputs)
    
    assert outputs['loan_schedule']['payment'].sum() == 0
    assert outputs['kpis']['debt_service'].sum() == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
