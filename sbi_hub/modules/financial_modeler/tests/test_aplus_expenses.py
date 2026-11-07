import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from sbi_hub.modules.financial_modeler.engine.model import build_model
from sbi_hub.modules.financial_modeler.engine.payroll import calculate_payroll
from sbi_hub.modules.financial_modeler.engine.opex import calculate_opex


def get_aplus_inputs(time_mode='monthly'):
    """Get model inputs with A+ expense architecture."""
    periods = 36 if time_mode == 'monthly' else 3
    
    return {
        'time_mode': time_mode,
        'periods': periods,
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 200.0,
                'volume': 200.0,
                'growth_rate': 0.10,
                'cogs_override': None
            }
        ],
        'global_cogs_pct': 0.30,
        'payroll_roles': [
            {
                'role': 'Production Worker',
                'headcount': 2,
                'pay_type': 'hourly',
                'rate': 25.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15,
                'role_type': 'direct'
            },
            {
                'role': 'Manager',
                'headcount': 1,
                'pay_type': 'salary',
                'rate': 60000.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15,
                'role_type': 'indirect'
            }
        ],
        'opex_items': [
            {
                'name': 'Rent',
                'amount': 2000.0,
                'growth_rate': 0.03,
                'category': 'fixed'
            },
            {
                'name': 'Utilities',
                'amount': 500.0,
                'growth_rate': 0.02,
                'category': 'semi-fixed'
            },
            {
                'name': 'Credit Card Fees',
                'amount': 0.03,
                'growth_rate': 0.0,
                'category': 'variable_pct_revenue'
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
        'annual_depreciation': 5000.0
    }


def test_direct_payroll_flows_to_cogs():
    """Test that direct payroll appears in COGS."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert 'cogs_direct_labor' in pnl.columns
    assert 'cogs_total' in pnl.columns
    
    assert (pnl['cogs_direct_labor'] > 0).any()
    
    assert (pnl['cogs_total'] == pnl['cogs_materials'] + pnl['cogs_direct_labor']).all()


def test_indirect_payroll_flows_to_opex():
    """Test that indirect payroll appears in operating expenses."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert 'indirect_payroll' in pnl.columns
    
    assert (pnl['indirect_payroll'] > 0).any()
    
    assert (pnl['operating_expenses'] == pnl['indirect_payroll'] + pnl['opex']).all()


def test_payroll_direct_indirect_split():
    """Test that payroll correctly splits between direct and indirect."""
    inputs = get_aplus_inputs('monthly')
    
    payroll_df = calculate_payroll(
        inputs['payroll_roles'],
        inputs['time_mode'],
        inputs['periods']
    )
    
    assert 'direct_total' in payroll_df.columns
    assert 'indirect_total' in payroll_df.columns
    
    assert (payroll_df['direct_total'] > 0).all()
    assert (payroll_df['indirect_total'] > 0).all()
    
    assert (payroll_df['total'] == payroll_df['direct_total'] + payroll_df['indirect_total']).all()


def test_variable_percent_expense_scales_with_revenue():
    """Test that variable % revenue expenses scale properly with revenue."""
    inputs = get_aplus_inputs('monthly')
    
    outputs = build_model(inputs)
    
    revenue = outputs['revenue_df']['total']
    opex_df = outputs['opex_df']
    
    assert 'Credit Card Fees' in opex_df.columns
    
    expected_fees = revenue * 0.03
    
    assert np.allclose(opex_df['Credit Card Fees'], expected_fees, rtol=1e-5)


def test_opex_category_totals():
    """Test that opex categories are properly totaled."""
    inputs = get_aplus_inputs('monthly')
    
    revenue = pd.Series([40000.0] * inputs['periods'], index=range(inputs['periods']))
    
    opex_df = calculate_opex(
        inputs['opex_items'],
        inputs['time_mode'],
        inputs['periods'],
        revenue
    )
    
    assert 'fixed_total' in opex_df.columns
    assert 'semi_fixed_total' in opex_df.columns
    assert 'variable_total' in opex_df.columns
    
    assert (opex_df['fixed_total'] > 0).all()
    assert (opex_df['semi_fixed_total'] > 0).all()
    assert (opex_df['variable_total'] > 0).all()
    
    assert (opex_df['total'] == opex_df['fixed_total'] + opex_df['semi_fixed_total'] + opex_df['variable_total']).all()


def test_growth_compounding_correct():
    """Test that growth rates compound correctly over periods."""
    inputs = get_aplus_inputs('monthly')
    
    opex_df = calculate_opex(
        inputs['opex_items'],
        inputs['time_mode'],
        inputs['periods'],
        None
    )
    
    rent_period_0 = opex_df['Rent'].iloc[0]
    rent_period_12 = opex_df['Rent'].iloc[12]
    
    monthly_growth = (1 + 0.03) ** (1/12) - 1
    expected_rent_period_12 = 2000.0 * (1 + monthly_growth) ** 12
    
    assert np.isclose(rent_period_12, expected_rent_period_12, rtol=1e-5)


def test_gross_margin_calculation():
    """Test that gross margin % is calculated correctly."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    pnl = outputs['pnl_statement']
    
    assert 'gross_margin' in kpis.columns
    
    for i in kpis.index:
        if pnl['revenue'].iloc[i] > 0:
            expected_margin = pnl['gross_profit'].iloc[i] / pnl['revenue'].iloc[i]
            assert np.isclose(kpis['gross_margin'].iloc[i], expected_margin, rtol=1e-5)


def test_overhead_load_calculation():
    """Test that overhead load % is calculated correctly."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    pnl = outputs['pnl_statement']
    
    assert 'overhead_load' in kpis.columns
    
    for i in kpis.index:
        if pnl['revenue'].iloc[i] > 0:
            expected_load = pnl['operating_expenses'].iloc[i] / pnl['revenue'].iloc[i]
            assert np.isclose(kpis['overhead_load'].iloc[i], expected_load, rtol=1e-5)


def test_payroll_pct_revenue_calculation():
    """Test that payroll % revenue is calculated correctly."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    pnl = outputs['pnl_statement']
    
    assert 'payroll_pct_revenue' in kpis.columns
    
    for i in kpis.index:
        if pnl['revenue'].iloc[i] > 0:
            total_payroll = pnl['cogs_direct_labor'].iloc[i] + pnl['indirect_payroll'].iloc[i]
            expected_pct = total_payroll / pnl['revenue'].iloc[i]
            assert np.isclose(kpis['payroll_pct_revenue'].iloc[i], expected_pct, rtol=1e-5)


def test_contribution_margin_calculation():
    """Test that contribution margin % is calculated correctly."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    pnl = outputs['pnl_statement']
    
    assert 'contribution_margin' in kpis.columns
    
    for i in kpis.index:
        if pnl['revenue'].iloc[i] > 0:
            contribution = pnl['gross_profit'].iloc[i] - pnl['indirect_payroll'].iloc[i]
            expected_margin = contribution / pnl['revenue'].iloc[i]
            assert np.isclose(kpis['contribution_margin'].iloc[i], expected_margin, rtol=1e-5)


def test_pnl_structure_aplus():
    """Test that P&L has all A+ architecture columns."""
    inputs = get_aplus_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    required_columns = [
        'revenue',
        'cogs_materials',
        'cogs_direct_labor',
        'cogs_total',
        'gross_profit',
        'indirect_payroll',
        'opex',
        'operating_expenses',
        'ebitda',
        'depreciation',
        'ebit',
        'interest',
        'pre_tax_income',
        'taxes',
        'net_income'
    ]
    
    for col in required_columns:
        assert col in pnl.columns


def test_backward_compatibility_no_role_type():
    """Test that payroll works without role_type field (backward compatibility)."""
    inputs = get_aplus_inputs('monthly')
    
    for role in inputs['payroll_roles']:
        del role['role_type']
    
    payroll_df = calculate_payroll(
        inputs['payroll_roles'],
        inputs['time_mode'],
        inputs['periods']
    )
    
    assert (payroll_df['direct_total'] == 0).all()
    assert (payroll_df['indirect_total'] > 0).all()


def test_backward_compatibility_no_category():
    """Test that opex works without category field (backward compatibility)."""
    inputs = get_aplus_inputs('monthly')
    
    for item in inputs['opex_items']:
        del item['category']
    
    revenue = pd.Series([40000.0] * inputs['periods'], index=range(inputs['periods']))
    
    opex_df = calculate_opex(
        inputs['opex_items'],
        inputs['time_mode'],
        inputs['periods'],
        revenue
    )
    
    assert (opex_df['fixed_total'] > 0).all()
    assert (opex_df['semi_fixed_total'] == 0).all()
    assert (opex_df['variable_total'] == 0).all()


def test_annual_mode_aplus():
    """Test A+ architecture works in annual mode."""
    inputs = get_aplus_inputs('annual')
    outputs = build_model(inputs)
    
    assert len(outputs['pnl_statement']) == 3
    assert (outputs['pnl_statement']['cogs_direct_labor'] > 0).any()
    assert (outputs['pnl_statement']['indirect_payroll'] > 0).any()


def test_no_negative_taxes_aplus():
    """Test that taxes are never negative in A+ architecture."""
    inputs = get_aplus_inputs('monthly')
    
    inputs['revenue_streams'][0]['volume'] = 10.0
    
    outputs = build_model(inputs)
    pnl = outputs['pnl_statement']
    
    assert (pnl['taxes'] >= 0).all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
