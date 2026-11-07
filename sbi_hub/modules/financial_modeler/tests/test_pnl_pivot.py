import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
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


def test_pnl_transpose_structure():
    """Test that P&L can be transposed for financial statement layout."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    # Original: periods as rows, line items as columns
    assert pnl.shape[0] == 12  # 12 periods (rows)
    assert pnl.shape[1] == 15  # 15 line items (columns)
    
    # Transpose: line items as rows, periods as columns
    pnl_transposed = pnl.T
    
    assert pnl_transposed.shape[0] == 15  # 15 line items (rows)
    assert pnl_transposed.shape[1] == 12  # 12 periods (columns)
    
    # Verify all line items present
    expected_line_items = [
        'revenue', 'cogs_materials', 'cogs_direct_labor', 'cogs_total',
        'gross_profit', 'indirect_payroll', 'opex', 'operating_expenses',
        'ebitda', 'depreciation', 'ebit', 'interest', 'pre_tax_income',
        'taxes', 'net_income'
    ]
    
    for item in expected_line_items:
        assert item in pnl_transposed.index


def test_pnl_transpose_values_preserved():
    """Test that transposing P&L preserves all values."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Check that values are preserved
    for period in range(12):
        for line_item in pnl.columns:
            original_value = pnl.loc[period, line_item]
            transposed_value = pnl_transposed.loc[line_item, period]
            assert original_value == transposed_value


def test_pnl_transpose_annual_mode():
    """Test that P&L transpose works in annual mode."""
    inputs = get_test_inputs('annual')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    assert pnl_transposed.shape[0] == 15  # 15 line items (rows)
    assert pnl_transposed.shape[1] == 5   # 5 periods (columns)


def test_pnl_row_labels():
    """Test that row labels can be mapped to clean financial terminology."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Apply clean labels
    row_labels = {
        'revenue': 'Revenue',
        'cogs_materials': 'COGS - Materials',
        'cogs_direct_labor': 'COGS - Direct Labor',
        'cogs_total': 'Total COGS',
        'gross_profit': 'Gross Profit',
        'indirect_payroll': 'Indirect Payroll',
        'opex': 'Operating Expenses',
        'operating_expenses': 'Total Operating Expenses',
        'ebitda': 'EBITDA',
        'depreciation': 'Depreciation',
        'ebit': 'EBIT',
        'interest': 'Interest Expense',
        'pre_tax_income': 'Pre-Tax Income',
        'taxes': 'Taxes',
        'net_income': 'Net Income'
    }
    
    pnl_labeled = pnl_transposed.copy()
    pnl_labeled.index = pnl_labeled.index.map(lambda x: row_labels.get(x, x))
    
    # Verify clean labels applied
    assert 'Revenue' in pnl_labeled.index
    assert 'COGS - Materials' in pnl_labeled.index
    assert 'Total COGS' in pnl_labeled.index
    assert 'Gross Profit' in pnl_labeled.index
    assert 'EBITDA' in pnl_labeled.index
    assert 'Net Income' in pnl_labeled.index


def test_pnl_column_labels():
    """Test that period columns can be labeled."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Rename columns to Period 0, Period 1, etc.
    pnl_transposed.columns = [f'Period {i}' for i in pnl_transposed.columns]
    
    assert 'Period 0' in pnl_transposed.columns
    assert 'Period 1' in pnl_transposed.columns
    assert 'Period 11' in pnl_transposed.columns


def test_pnl_csv_export():
    """Test that transposed P&L can be exported to CSV."""
    inputs = get_test_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    pnl_transposed = pnl.T
    
    # Apply formatting
    pnl_transposed.columns = [f'Period {i}' for i in pnl_transposed.columns]
    row_labels = {
        'revenue': 'Revenue',
        'cogs_materials': 'COGS - Materials',
        'cogs_direct_labor': 'COGS - Direct Labor',
        'cogs_total': 'Total COGS',
        'gross_profit': 'Gross Profit',
        'indirect_payroll': 'Indirect Payroll',
        'opex': 'Operating Expenses',
        'operating_expenses': 'Total Operating Expenses',
        'ebitda': 'EBITDA',
        'depreciation': 'Depreciation',
        'ebit': 'EBIT',
        'interest': 'Interest Expense',
        'pre_tax_income': 'Pre-Tax Income',
        'taxes': 'Taxes',
        'net_income': 'Net Income'
    }
    pnl_transposed.index = pnl_transposed.index.map(lambda x: row_labels.get(x, x))
    pnl_transposed.index.name = 'Line Item'
    
    # Export to CSV
    csv_string = pnl_transposed.to_csv()
    
    # Verify CSV contains expected content
    assert 'Line Item' in csv_string
    assert 'Period 0' in csv_string
    assert 'Revenue' in csv_string
    assert 'EBITDA' in csv_string
    assert 'Net Income' in csv_string


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
