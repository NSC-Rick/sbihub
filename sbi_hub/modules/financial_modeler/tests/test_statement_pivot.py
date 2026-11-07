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


def test_income_statement_transpose_structure():
    """Test that Income Statement can be transposed for financial statement layout."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    
    # Original: periods as rows, line items as columns
    assert income.shape[0] == 12  # 12 periods (rows)
    
    # Transpose: line items as rows, periods as columns
    income_transposed = income.T
    
    assert income_transposed.shape[1] == 12  # 12 periods (columns)
    
    # Verify revenue is present
    assert 'revenue' in income_transposed.index


def test_income_statement_transpose_values_preserved():
    """Test that transposing Income Statement preserves all values."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    income_transposed = income.T
    
    # Check that values are preserved
    for period in range(12):
        for line_item in income.columns:
            original_value = income.loc[period, line_item]
            transposed_value = income_transposed.loc[line_item, period]
            assert original_value == transposed_value


def test_income_statement_percent_of_revenue():
    """Test that Income Statement % of revenue calculation works."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    income_transposed = income.T
    
    # Rename columns
    income_transposed.columns = [f'Period {i}' for i in income_transposed.columns]
    
    # Convert to % of revenue
    income_percent = income_transposed.copy()
    for col_idx, period in enumerate(income_percent.columns):
        revenue = income['revenue'].iloc[col_idx]
        if revenue != 0:
            income_percent[period] = (income_transposed[period] / revenue) * 100
    
    # Revenue should be 100%
    assert np.isclose(income_percent.loc['revenue', 'Period 0'], 100.0, rtol=1e-5)


def test_cash_flow_transpose_structure():
    """Test that Cash Flow Statement can be transposed for financial statement layout."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    cash_flow = outputs['cash_flow_statement']
    
    # Original: periods as rows, line items as columns
    assert cash_flow.shape[0] == 12  # 12 periods (rows)
    
    # Transpose: line items as rows, periods as columns
    cash_flow_transposed = cash_flow.T
    
    assert cash_flow_transposed.shape[1] == 12  # 12 periods (columns)
    
    # Verify key items are present
    assert 'net_income' in cash_flow_transposed.index
    assert 'ending_cash' in cash_flow_transposed.index


def test_cash_flow_transpose_values_preserved():
    """Test that transposing Cash Flow Statement preserves all values."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    cash_flow = outputs['cash_flow_statement']
    cash_flow_transposed = cash_flow.T
    
    # Check that values are preserved
    for period in range(12):
        for line_item in cash_flow.columns:
            original_value = cash_flow.loc[period, line_item]
            transposed_value = cash_flow_transposed.loc[line_item, period]
            assert original_value == transposed_value


def test_income_statement_annual_mode():
    """Test that Income Statement transpose works in annual mode."""
    inputs = get_test_inputs('annual')
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    income_transposed = income.T
    
    assert income_transposed.shape[1] == 5  # 5 periods (columns)


def test_cash_flow_annual_mode():
    """Test that Cash Flow Statement transpose works in annual mode."""
    inputs = get_test_inputs('annual')
    outputs = build_model(inputs)
    
    cash_flow = outputs['cash_flow_statement']
    cash_flow_transposed = cash_flow.T
    
    assert cash_flow_transposed.shape[1] == 5  # 5 periods (columns)


def test_income_statement_column_labels():
    """Test that Income Statement period columns can be labeled."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    income_transposed = income.T
    
    # Rename columns to Period 0, Period 1, etc.
    income_transposed.columns = [f'Period {i}' for i in income_transposed.columns]
    
    assert 'Period 0' in income_transposed.columns
    assert 'Period 1' in income_transposed.columns
    assert 'Period 11' in income_transposed.columns


def test_cash_flow_column_labels():
    """Test that Cash Flow Statement period columns can be labeled."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    cash_flow = outputs['cash_flow_statement']
    cash_flow_transposed = cash_flow.T
    
    # Rename columns to Period 0, Period 1, etc.
    cash_flow_transposed.columns = [f'Period {i}' for i in cash_flow_transposed.columns]
    
    assert 'Period 0' in cash_flow_transposed.columns
    assert 'Period 1' in cash_flow_transposed.columns
    assert 'Period 11' in cash_flow_transposed.columns


def test_income_statement_csv_export():
    """Test that transposed Income Statement can be exported to CSV."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    income_transposed = income.T
    
    # Apply formatting
    income_transposed.columns = [f'Period {i}' for i in income_transposed.columns]
    income_transposed.index.name = 'Line Item'
    
    # Export to CSV
    csv_string = income_transposed.to_csv()
    
    # Verify CSV contains expected content
    assert 'Line Item' in csv_string
    assert 'Period 0' in csv_string
    assert 'revenue' in csv_string


def test_cash_flow_csv_export():
    """Test that transposed Cash Flow Statement can be exported to CSV."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    cash_flow = outputs['cash_flow_statement']
    cash_flow_transposed = cash_flow.T
    
    # Apply formatting
    cash_flow_transposed.columns = [f'Period {i}' for i in cash_flow_transposed.columns]
    cash_flow_transposed.index.name = 'Line Item'
    
    # Export to CSV
    csv_string = cash_flow_transposed.to_csv()
    
    # Verify CSV contains expected content
    assert 'Line Item' in csv_string
    assert 'Period 0' in csv_string
    assert 'net_income' in csv_string
    assert 'ending_cash' in csv_string


def test_income_statement_percent_divide_by_zero():
    """Test that Income Statement % of revenue handles zero revenue."""
    inputs = get_test_inputs('monthly')
    inputs['revenue_streams'][0]['volume'] = 0.0  # Zero revenue
    
    outputs = build_model(inputs)
    
    income = outputs['income_statement']
    income_transposed = income.T
    
    # Rename columns
    income_transposed.columns = [f'Period {i}' for i in income_transposed.columns]
    
    # Convert to % of revenue with zero revenue
    income_percent = income_transposed.copy()
    for col_idx, period in enumerate(income_percent.columns):
        revenue = income['revenue'].iloc[col_idx]
        if revenue != 0:
            income_percent[period] = (income_transposed[period] / revenue) * 100
        else:
            # Should set to 0 when revenue is 0
            income_percent[period] = 0
    
    # All values should be 0 when revenue is 0
    for period in income_percent.columns:
        for line_item in income_percent.index:
            assert income_percent.loc[line_item, period] == 0


def test_statements_match_pnl_orientation():
    """Test that Income and Cash Flow statements match P&L orientation."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    # Get all three statements
    income = outputs['income_statement']
    pnl = outputs['pnl_statement']
    cash_flow = outputs['cash_flow_statement']
    
    # Transpose all
    income_t = income.T
    pnl_t = pnl.T
    cash_flow_t = cash_flow.T
    
    # All should have same number of period columns
    assert income_t.shape[1] == pnl_t.shape[1] == cash_flow_t.shape[1] == 12
    
    # All should have line items as rows
    assert income_t.shape[0] > 0
    assert pnl_t.shape[0] > 0
    assert cash_flow_t.shape[0] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
