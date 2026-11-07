import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from sbi_hub.modules.financial_modeler.engine.model import build_model
from sbi_hub.modules.financial_modeler.engine.underwriting import (
    calculate_dscr,
    calculate_contribution_margin,
    calculate_break_even_revenue,
    apply_owner_compensation_to_payroll,
    calculate_owner_distribution
)


def get_underwriting_inputs(time_mode='monthly', owner_mode='distribution', owner_amount=60000.0):
    """Get model inputs with underwriting features."""
    periods = 36 if time_mode == 'monthly' else 3
    
    return {
        'time_mode': time_mode,
        'periods': periods,
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 200.0,
                'volume': 300.0,
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
                'rate': 50000.0,
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
                'name': 'Credit Card Fees',
                'amount': 0.03,
                'growth_rate': 0.0,
                'category': 'variable_pct_revenue'
            }
        ],
        'loan_principal': 100000.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 5000.0,
        'owner_compensation': {
            'mode': owner_mode,
            'amount': owner_amount
        }
    }


def test_dscr_formula_correct():
    """Test that DSCR = EBITDA / Total Debt Service."""
    inputs = get_underwriting_inputs('monthly', 'distribution', 0.0)
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    
    assert 'dscr' in kpis.columns
    
    for i in kpis.index:
        ebitda = kpis['ebitda'].iloc[i]
        debt_service = kpis['debt_service'].iloc[i]
        dscr = kpis['dscr'].iloc[i]
        
        if debt_service > 0:
            expected_dscr = ebitda / debt_service
            assert np.isclose(dscr, expected_dscr, rtol=1e-5)
        else:
            assert dscr == 0


def test_owner_payroll_affects_ebitda():
    """Test that owner compensation as payroll affects EBITDA."""
    inputs_no_owner = get_underwriting_inputs('monthly', 'distribution', 0.0)
    inputs_owner_payroll = get_underwriting_inputs('monthly', 'payroll', 60000.0)
    
    outputs_no_owner = build_model(inputs_no_owner)
    outputs_owner_payroll = build_model(inputs_owner_payroll)
    
    ebitda_no_owner = outputs_no_owner['pnl_statement']['ebitda'].iloc[0]
    ebitda_owner_payroll = outputs_owner_payroll['pnl_statement']['ebitda'].iloc[0]
    
    assert ebitda_owner_payroll < ebitda_no_owner
    
    indirect_payroll_no_owner = outputs_no_owner['pnl_statement']['indirect_payroll'].iloc[0]
    indirect_payroll_owner = outputs_owner_payroll['pnl_statement']['indirect_payroll'].iloc[0]
    
    assert indirect_payroll_owner > indirect_payroll_no_owner


def test_owner_distribution_affects_cash_only():
    """Test that owner compensation as distribution affects only cash flow, not EBITDA."""
    inputs_no_owner = get_underwriting_inputs('monthly', 'distribution', 0.0)
    inputs_owner_dist = get_underwriting_inputs('monthly', 'distribution', 60000.0)
    
    outputs_no_owner = build_model(inputs_no_owner)
    outputs_owner_dist = build_model(inputs_owner_dist)
    
    ebitda_no_owner = outputs_no_owner['pnl_statement']['ebitda'].iloc[0]
    ebitda_owner_dist = outputs_owner_dist['pnl_statement']['ebitda'].iloc[0]
    
    assert np.isclose(ebitda_no_owner, ebitda_owner_dist, rtol=1e-5)
    
    ending_cash_no_owner = outputs_no_owner['cash_flow_statement']['ending_cash'].iloc[-1]
    ending_cash_owner_dist = outputs_owner_dist['cash_flow_statement']['ending_cash'].iloc[-1]
    
    assert ending_cash_owner_dist < ending_cash_no_owner
    
    assert 'owner_distribution' in outputs_owner_dist['cash_flow_statement'].columns
    total_owner_dist = outputs_owner_dist['cash_flow_statement']['owner_distribution'].sum()
    # 36 months = 3 years, so total = 3 × annual amount
    assert np.isclose(total_owner_dist, 60000.0 * 3, rtol=1e-5)


def test_break_even_includes_debt_and_owner():
    """Test that break-even revenue includes debt service and owner salary."""
    inputs = get_underwriting_inputs('monthly', 'distribution', 60000.0)
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    
    assert 'break_even_revenue' in kpis.columns
    assert 'fixed_cost_base' in kpis.columns
    
    break_even = kpis['break_even_revenue'].iloc[0]
    fixed_cost_base = kpis['fixed_cost_base'].iloc[0]
    
    assert not pd.isna(break_even)
    assert break_even > 0
    
    annual_debt_service = outputs['loan_schedule']['payment'].sum()
    owner_salary = 60000.0
    
    assert fixed_cost_base > annual_debt_service
    assert fixed_cost_base > owner_salary


def test_contribution_margin_calculation():
    """Test that contribution margin is calculated correctly."""
    inputs = get_underwriting_inputs('monthly')
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    
    assert 'contribution_margin_pct' in kpis.columns
    
    pnl = outputs['pnl_statement']
    opex_df = outputs['opex_df']
    
    for i in kpis.index:
        revenue = pnl['revenue'].iloc[i]
        cogs_total = pnl['cogs_total'].iloc[i]
        variable_opex = opex_df['variable_total'].iloc[i] if 'variable_total' in opex_df.columns else 0
        
        variable_costs = cogs_total + variable_opex
        
        if revenue > 0:
            expected_contrib_margin = (revenue - variable_costs) / revenue
            assert np.isclose(kpis['contribution_margin_pct'].iloc[i], expected_contrib_margin, rtol=1e-5)


def test_owner_payroll_mode_adds_to_payroll_roles():
    """Test that owner payroll mode adds owner to payroll roles."""
    owner_comp = {'mode': 'payroll', 'amount': 60000.0}
    payroll_roles = [
        {
            'role': 'Manager',
            'headcount': 1,
            'pay_type': 'salary',
            'rate': 50000.0,
            'hours_per_week': 40,
            'annual_raise_pct': 0.03,
            'payroll_tax_pct': 0.0765,
            'benefits_pct': 0.15,
            'role_type': 'indirect'
        }
    ]
    
    updated_roles = apply_owner_compensation_to_payroll(payroll_roles, owner_comp, 'monthly')
    
    assert len(updated_roles) == 2
    assert updated_roles[-1]['role'] == 'Owner'
    assert updated_roles[-1]['rate'] == 60000.0
    assert updated_roles[-1]['role_type'] == 'indirect'


def test_owner_distribution_mode_no_payroll_change():
    """Test that owner distribution mode does not change payroll roles."""
    owner_comp = {'mode': 'distribution', 'amount': 60000.0}
    payroll_roles = [
        {
            'role': 'Manager',
            'headcount': 1,
            'pay_type': 'salary',
            'rate': 50000.0,
            'hours_per_week': 40,
            'annual_raise_pct': 0.03,
            'payroll_tax_pct': 0.0765,
            'benefits_pct': 0.15,
            'role_type': 'indirect'
        }
    ]
    
    updated_roles = apply_owner_compensation_to_payroll(payroll_roles, owner_comp, 'monthly')
    
    assert len(updated_roles) == 1
    assert updated_roles == payroll_roles


def test_owner_distribution_monthly_calculation():
    """Test that owner distribution is calculated correctly for monthly mode."""
    owner_comp = {'mode': 'distribution', 'amount': 60000.0}
    
    owner_dist = calculate_owner_distribution(owner_comp, 'monthly', 36)
    
    assert len(owner_dist) == 36
    # Annual amount / 12 = monthly amount
    assert np.allclose(owner_dist, 5000.0, rtol=1e-5)
    # Total distribution over 3 years should equal 3 × annual amount
    total_distribution = owner_dist.sum()
    expected_total = 60000.0 * 3  # 3 years
    
    assert np.isclose(total_distribution, expected_total, rtol=1e-5)


def test_owner_distribution_annual_calculation():
    """Test that owner distribution is calculated correctly for annual mode."""
    owner_comp = {'mode': 'distribution', 'amount': 60000.0}
    
    owner_dist = calculate_owner_distribution(owner_comp, 'annual', 3)
    
    assert len(owner_dist) == 3
    assert np.allclose(owner_dist, 60000.0, rtol=1e-5)


def test_dscr_zero_debt_service():
    """Test that DSCR is None when debt service is zero (debt-free scenario)."""
    ebitda = pd.Series([10000, 20000, 30000], index=range(3))
    debt_service = pd.Series([0, 0, 0], index=range(3))
    
    dscr = calculate_dscr(ebitda, debt_service, 'monthly')
    
    assert dscr.isna().all()  # All values should be None


def test_break_even_zero_contribution_margin():
    """Test that break-even returns NaN when contribution margin is zero or negative."""
    break_even = calculate_break_even_revenue(
        indirect_payroll=50000,
        fixed_opex=24000,
        semi_fixed_opex=6000,
        owner_salary_annual=60000,
        annual_debt_service=20000,
        contribution_margin_pct=0.0,
        time_mode='monthly'
    )
    
    assert pd.isna(break_even)
    
    break_even_negative = calculate_break_even_revenue(
        indirect_payroll=50000,
        fixed_opex=24000,
        semi_fixed_opex=6000,
        owner_salary_annual=60000,
        annual_debt_service=20000,
        contribution_margin_pct=-0.1,
        time_mode='monthly'
    )
    
    assert pd.isna(break_even_negative)


def test_annual_mode_underwriting():
    """Test underwriting metrics work in annual mode."""
    inputs = get_underwriting_inputs('annual')
    outputs = build_model(inputs)
    
    pnl = outputs['pnl_statement']
    
    assert len(pnl) == 3
    assert 'dscr' in outputs['kpis'].columns
    assert 'break_even_revenue' in outputs['kpis'].columns


def test_no_owner_compensation():
    """Test that zero owner compensation works correctly."""
    inputs = get_underwriting_inputs('monthly', 'distribution', 0.0)
    outputs = build_model(inputs)
    
    assert 'owner_distribution' in outputs['cash_flow_statement'].columns
    assert (outputs['cash_flow_statement']['owner_distribution'] == 0).all()


def test_owner_no_double_count():
    """Test that owner salary is not double-counted in payroll and distribution."""
    inputs_payroll = get_underwriting_inputs('monthly', 'payroll', 60000.0)
    outputs_payroll = build_model(inputs_payroll)
    
    assert (outputs_payroll['cash_flow_statement']['owner_distribution'] == 0).all()
    
    inputs_dist = get_underwriting_inputs('monthly', 'distribution', 60000.0)
    outputs_dist = build_model(inputs_dist)
    
    payroll_no_owner = outputs_dist['payroll_df']['indirect_total'].iloc[0]
    payroll_with_owner = outputs_payroll['payroll_df']['indirect_total'].iloc[0]
    
    assert payroll_with_owner > payroll_no_owner


def test_break_even_formula_components():
    """Test that break-even formula includes all required components."""
    inputs = get_underwriting_inputs('monthly', 'distribution', 60000.0)
    outputs = build_model(inputs)
    
    kpis = outputs['kpis']
    fixed_cost_base = kpis['fixed_cost_base'].iloc[0]
    
    annual_indirect_payroll = outputs['pnl_statement']['indirect_payroll'].sum()
    annual_fixed_opex = outputs['opex_df']['fixed_total'].sum()
    annual_semi_fixed_opex = outputs['opex_df']['semi_fixed_total'].sum() if 'semi_fixed_total' in outputs['opex_df'].columns else 0
    annual_debt_service = outputs['loan_schedule']['payment'].sum()
    owner_salary = 60000.0
    
    expected_fixed_cost_base = (
        annual_indirect_payroll +
        annual_fixed_opex +
        annual_semi_fixed_opex +
        owner_salary +
        annual_debt_service
    )
    
    assert np.isclose(fixed_cost_base, expected_fixed_cost_base, rtol=1e-3)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
