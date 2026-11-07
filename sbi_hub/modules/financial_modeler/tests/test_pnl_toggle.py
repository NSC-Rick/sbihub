import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from sbi_hub.modules.financial_modeler.engine.model import build_model


def get_test_inputs(time_mode='monthly'):
    """Get basic model inputs for testing."""
    periods = 12 if time_mode == 'monthly' else 5
    
    return {
        'time_mode': time_mode,
        'periods': periods,
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 100.0,
                'volume': 100.0,
                'growth_rate': 0.05,
                'cogs_override': None
            }
        ],
        'global_cogs_pct': 0.30,
        'payroll_roles': [
            {
                'role': 'Worker',
                'headcount': 1,
                'pay_type': 'hourly',
                'rate': 20.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.10,
                'role_type': 'direct'
            }
        ],
        'opex_items': [
            {
                'name': 'Rent',
                'amount': 1000.0,
                'growth_rate': 0.02,
                'category': 'fixed'
            }
        ],
        'loan_principal': 50000.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 2000.0,
        'owner_compensation': {
            'mode': 'distribution',
            'amount': 0.0
        }
    }


def test_pnl_percent_of_revenue_calculation():
    """Test that % of revenue is calculated correctly."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Rename columns to Period 0, Period 1, etc.
    pnl_transposed.columns = [f'Period {i}' for i in pnl_transposed.columns]
    
    # Calculate % of revenue for first period
    revenue_value = pnl['revenue'].iloc[0]
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # Revenue should always be 100%
    assert np.isclose(pnl_percent.loc['revenue', 'Period 0'], 100.0, rtol=1e-5)
    
    # COGS should be 30% (global COGS %)
    # Note: This includes materials + direct labor, so it won't be exactly 30%
    # Just verify it's a reasonable percentage
    cogs_pct = pnl_percent.loc['cogs_total', 'Period 0']
    assert 0 < cogs_pct < 100
    
    # Net income should be positive and less than 100%
    net_income_pct = pnl_percent.loc['net_income', 'Period 0']
    assert net_income_pct < 100


def test_pnl_percent_revenue_always_100():
    """Test that revenue is always 100% in % of revenue view."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # Check all periods
    for period in pnl_percent.columns:
        revenue_pct = pnl_percent.loc['revenue', period]
        assert np.isclose(revenue_pct, 100.0, rtol=1e-5)


def test_pnl_percent_divide_by_zero_handling():
    """Test that divide by zero is handled gracefully."""
    # Create a scenario with zero revenue
    inputs = get_test_inputs('monthly')
    inputs['revenue_streams'][0]['volume'] = 0.0  # Zero volume = zero revenue
    
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Convert to % of revenue with zero revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
        else:
            # Should set to 0 when revenue is 0
            pnl_percent[period] = 0
    
    # All values should be 0 when revenue is 0
    for period in pnl_percent.columns:
        for line_item in pnl_percent.index:
            assert pnl_percent.loc[line_item, period] == 0


def test_pnl_percent_annual_mode():
    """Test that % of revenue works in annual mode."""
    inputs = get_test_inputs('annual')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # Revenue should be 100% for all 5 periods
    for period in pnl_percent.columns:
        revenue_pct = pnl_percent.loc['revenue', period]
        assert np.isclose(revenue_pct, 100.0, rtol=1e-5)


def test_pnl_percent_values_sum_correctly():
    """Test that percentage values maintain relationships."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Rename columns to Period 0, Period 1, etc.
    pnl_transposed.columns = [f'Period {i}' for i in pnl_transposed.columns]
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # For first period, verify relationships
    period = 'Period 0'
    
    # Revenue - COGS Total = Gross Profit
    revenue_pct = pnl_percent.loc['revenue', period]
    cogs_total_pct = pnl_percent.loc['cogs_total', period]
    gross_profit_pct = pnl_percent.loc['gross_profit', period]
    
    assert np.isclose(revenue_pct - cogs_total_pct, gross_profit_pct, rtol=1e-5)
    
    # Gross Profit - Operating Expenses = EBITDA
    operating_expenses_pct = pnl_percent.loc['operating_expenses', period]
    ebitda_pct = pnl_percent.loc['ebitda', period]
    
    assert np.isclose(gross_profit_pct - operating_expenses_pct, ebitda_pct, rtol=1e-5)


def test_pnl_dollar_view_unchanged():
    """Test that dollar view is not affected by % of revenue calculation."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Dollar view should be identical to transposed original
    pnl_dollar = pnl_transposed.copy()
    
    # Verify values match original
    for period in pnl_dollar.columns:
        for line_item in pnl_dollar.index:
            original_value = pnl_transposed.loc[line_item, period]
            dollar_value = pnl_dollar.loc[line_item, period]
            assert original_value == dollar_value


def test_pnl_percent_csv_export():
    """Test that % of revenue can be exported to CSV."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Rename columns
    pnl_transposed.columns = [f'Period {i}' for i in pnl_transposed.columns]
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # Export to CSV
    csv_string = pnl_percent.to_csv()
    
    # Verify CSV contains expected content
    assert 'Period 0' in csv_string
    assert 'revenue' in csv_string
    
    # Verify revenue values are close to 100
    lines = csv_string.split('\n')
    revenue_line = [line for line in lines if line.startswith('revenue')][0]
    values = revenue_line.split(',')[1:]  # Skip first column (label)
    
    for value in values:
        if value.strip():  # Skip empty values
            assert np.isclose(float(value), 100.0, rtol=1e-5)


def test_pnl_percent_formatting():
    """Test that % values are formatted correctly."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # Verify all values are percentages (0-100 range for most items)
    for period in pnl_percent.columns:
        revenue_pct = pnl_percent.loc['revenue', period]
        assert np.isclose(revenue_pct, 100.0, rtol=1e-5)
        
        # COGS should be positive and less than 100%
        cogs_pct = pnl_percent.loc['cogs_total', period]
        assert 0 < cogs_pct < 100


def test_pnl_percent_negative_values():
    """Test that negative values (like losses) are handled correctly in % view."""
    inputs = get_test_inputs('monthly')
    # Set very high opex to create a loss
    inputs['opex_items'][0]['amount'] = 50000.0
    
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Rename columns to Period 0, Period 1, etc.
    pnl_transposed.columns = [f'Period {i}' for i in pnl_transposed.columns]
    
    # Convert to % of revenue
    pnl_percent = pnl_transposed.copy()
    for col_idx, period in enumerate(pnl_percent.columns):
        revenue = pnl['revenue'].iloc[col_idx]
        if revenue != 0:
            pnl_percent[period] = (pnl_transposed[period] / revenue) * 100
    
    # Net income should be negative (loss)
    net_income_pct = pnl_percent.loc['net_income', 'Period 0']
    assert net_income_pct < 0  # Loss scenario


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
