import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from sbi_hub.modules.financial_modeler.engine.model import build_model


def get_profitable_inputs(time_mode='monthly'):
    """Get model inputs that result in positive income."""
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
                'role': 'Manager',
                'headcount': 1,
                'pay_type': 'salary',
                'rate': 50000.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15
            }
        ],
        'opex_items': [
            {
                'name': 'Rent',
                'amount': 1000.0,
                'growth_rate': 0.03
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


def get_unprofitable_inputs(time_mode='monthly'):
    """Get model inputs that result in negative income."""
    periods = 36 if time_mode == 'monthly' else 3
    
    return {
        'time_mode': time_mode,
        'periods': periods,
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 50.0,
                'volume': 50.0,
                'growth_rate': 0.05,
                'cogs_override': None
            }
        ],
        'global_cogs_pct': 0.40,
        'payroll_roles': [
            {
                'role': 'Manager',
                'headcount': 2,
                'pay_type': 'salary',
                'rate': 80000.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15
            }
        ],
        'opex_items': [
            {
                'name': 'Rent',
                'amount': 5000.0,
                'growth_rate': 0.03
            }
        ],
        'loan_principal': 100000.0,
        'loan_annual_rate': 0.08,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 10000.0
    }


def test_pnl_positive_tax_monthly():
    """Test P&L with positive income generates positive taxes in monthly mode."""
    inputs = get_profitable_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert 'pnl_statement' in outputs
    assert len(pnl) == 36
    assert 'depreciation' in pnl.columns
    assert 'taxes' in pnl.columns
    assert 'pre_tax_income' in pnl.columns
    assert 'net_income' in pnl.columns
    
    assert (pnl['depreciation'] >= 0).all()
    assert (pnl['taxes'] >= 0).all()
    
    positive_income_periods = pnl[pnl['pre_tax_income'] > 0]
    if len(positive_income_periods) > 0:
        assert (positive_income_periods['taxes'] > 0).all()


def test_pnl_positive_tax_annual():
    """Test P&L with positive income generates positive taxes in annual mode."""
    inputs = get_profitable_inputs('annual')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert len(pnl) == 3
    assert (pnl['depreciation'] >= 0).all()
    assert (pnl['taxes'] >= 0).all()


def test_pnl_negative_no_tax_monthly():
    """Test P&L with negative income generates zero taxes in monthly mode."""
    inputs = get_unprofitable_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert len(pnl) == 36
    
    negative_income_periods = pnl[pnl['pre_tax_income'] < 0]
    if len(negative_income_periods) > 0:
        assert (negative_income_periods['taxes'] == 0).all()


def test_pnl_negative_no_tax_annual():
    """Test P&L with negative income generates zero taxes in annual mode."""
    inputs = get_unprofitable_inputs('annual')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert len(pnl) == 3
    
    negative_income_periods = pnl[pnl['pre_tax_income'] < 0]
    if len(negative_income_periods) > 0:
        assert (negative_income_periods['taxes'] == 0).all()


def test_pnl_depreciation_monthly():
    """Test depreciation is correctly divided by 12 in monthly mode."""
    inputs = get_profitable_inputs('monthly')
    annual_dep = inputs['annual_depreciation']
    
    outputs = build_model(inputs)
    pnl = outputs['pnl_statement']
    
    expected_monthly_dep = annual_dep / 12
    
    assert np.allclose(pnl['depreciation'].iloc[0], expected_monthly_dep, rtol=1e-5)
    assert (pnl['depreciation'] == expected_monthly_dep).all()


def test_pnl_depreciation_annual():
    """Test depreciation equals annual amount in annual mode."""
    inputs = get_profitable_inputs('annual')
    annual_dep = inputs['annual_depreciation']
    
    outputs = build_model(inputs)
    pnl = outputs['pnl_statement']
    
    assert (pnl['depreciation'] == annual_dep).all()


def test_pnl_tax_calculation():
    """Test tax calculation is correct percentage of pre-tax income."""
    inputs = get_profitable_inputs('monthly')
    tax_rate = inputs['tax_rate']
    
    outputs = build_model(inputs)
    pnl = outputs['pnl_statement']
    
    for i in pnl.index:
        pre_tax = pnl['pre_tax_income'].iloc[i]
        tax = pnl['taxes'].iloc[i]
        
        if pre_tax > 0:
            expected_tax = pre_tax * tax_rate
            assert np.isclose(tax, expected_tax, rtol=1e-5)
        else:
            assert tax == 0


def test_pnl_net_income_calculation():
    """Test net income equals pre-tax income minus taxes."""
    inputs = get_profitable_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    for i in pnl.index:
        expected_net = pnl['pre_tax_income'].iloc[i] - pnl['taxes'].iloc[i]
        assert np.isclose(pnl['net_income'].iloc[i], expected_net, rtol=1e-5)


def test_pnl_ebit_calculation():
    """Test EBIT equals EBITDA minus depreciation."""
    inputs = get_profitable_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    for i in pnl.index:
        expected_ebit = pnl['ebitda'].iloc[i] - pnl['depreciation'].iloc[i]
        assert np.isclose(pnl['ebit'].iloc[i], expected_ebit, rtol=1e-5)


def test_pnl_no_nans():
    """Test P&L statement contains no NaN values."""
    inputs = get_profitable_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert not pnl.isnull().any().any()


def test_pnl_structure():
    """Test P&L statement has all required columns."""
    inputs = get_profitable_inputs('monthly')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    required_columns = [
        'revenue', 'cogs_materials', 'cogs_direct_labor', 'cogs_total', 
        'gross_profit', 'indirect_payroll', 'opex',
        'operating_expenses', 'ebitda', 'depreciation', 'ebit',
        'interest', 'pre_tax_income', 'taxes', 'net_income'
    ]
    
    for col in required_columns:
        assert col in pnl.columns


def test_pnl_zero_depreciation():
    """Test P&L works correctly with zero depreciation."""
    inputs = get_profitable_inputs('monthly')
    inputs['annual_depreciation'] = 0.0
    
    outputs = build_model(inputs)
    pnl = outputs['pnl_statement']
    
    assert (pnl['depreciation'] == 0).all()
    assert (pnl['ebit'] == pnl['ebitda']).all()


def test_pnl_zero_tax_rate():
    """Test P&L works correctly with zero tax rate."""
    inputs = get_profitable_inputs('monthly')
    inputs['tax_rate'] = 0.0
    
    outputs = build_model(inputs)
    pnl = outputs['pnl_statement']
    
    assert (pnl['taxes'] == 0).all()
    assert (pnl['net_income'] == pnl['pre_tax_income']).all()


def test_kpis_include_pnl_metrics():
    """Test KPIs include net income, taxes, and net margin from P&L."""
    inputs = get_profitable_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    
    assert 'net_income' in kpis.columns
    assert 'taxes' in kpis.columns
    assert 'net_margin' in kpis.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
