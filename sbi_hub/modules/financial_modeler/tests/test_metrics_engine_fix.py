"""
Test Metrics Engine Fix (WPP-FME-022)

Validates that margin calculations, contribution margin, and break-even revenue
are calculated correctly according to standard financial formulas.
"""

import pytest
import pandas as pd
import numpy as np
from sbi_hub.modules.financial_modeler.engine.statements import safe_divide, calculate_margin, build_pnl_statement, calculate_kpis
from sbi_hub.modules.financial_modeler.engine.underwriting import calculate_contribution_margin, calculate_break_even_revenue


def test_safe_divide():
    """
    TEST: safe_divide helper function
    
    Expected:
    - Returns 0.0 when denominator is 0
    - Returns correct division otherwise
    """
    assert safe_divide(100, 0) == 0.0
    assert safe_divide(100, 0.0) == 0.0
    assert safe_divide(100, None) == 0.0
    assert safe_divide(100, 50) == 2.0
    assert safe_divide(23210, 105500) == pytest.approx(0.22, abs=0.01)
    
    print("✅ TEST PASSED: safe_divide works correctly")


def test_calculate_margin():
    """
    TEST: calculate_margin helper function
    
    Expected:
    - Returns 0.0 when revenue is 0
    - Returns correct margin otherwise
    """
    assert calculate_margin(23210, 0) == 0.0
    assert calculate_margin(23210, 105500) == pytest.approx(0.22, abs=0.01)
    assert calculate_margin(9947.67, 105500) == pytest.approx(0.0943, abs=0.001)
    assert calculate_margin(8456, 105500) == pytest.approx(0.0802, abs=0.001)
    
    print("✅ TEST PASSED: calculate_margin works correctly")


def test_margin_calculations():
    """
    TEST A: Margin calculations
    
    Inputs:
    revenue = 105500
    gross_profit = 23210
    ebitda = 9947.666666666666
    net_income = 8456
    
    Expected:
    gross_margin_pct ≈ 0.2200
    ebitda_margin_pct ≈ 0.0943
    net_margin_pct ≈ 0.0802
    """
    # Setup test data
    periods = 12
    revenue = pd.Series([105500.0] * periods, index=range(periods))
    cogs_materials = pd.Series([82290.0] * periods, index=range(periods))
    direct_payroll = pd.Series([0.0] * periods, index=range(periods))
    indirect_payroll = pd.Series([4088.33] * periods, index=range(periods))
    opex_total = pd.Series([9174.0] * periods, index=range(periods))
    interest_expense = pd.Series([1491.67] * periods, index=range(periods))
    
    # Build PNL statement
    pnl = build_pnl_statement(
        revenue,
        cogs_materials,
        direct_payroll,
        indirect_payroll,
        opex_total,
        interest_expense,
        annual_depreciation=0.0,
        tax_rate=0.0,
        time_mode='monthly',
        periods=periods
    )
    
    # Calculate KPIs (simplified - just need margins)
    from sbi_hub.modules.financial_modeler.engine.statements import calculate_kpis
    from sbi_hub.modules.financial_modeler.engine.loan import calculate_loan_schedule
    
    # Create dummy loan schedule
    loan_schedule = pd.DataFrame({
        'payment': pd.Series([1491.67] * periods, index=range(periods)),
        'principal': pd.Series([0.0] * periods, index=range(periods)),
        'interest': pd.Series([1491.67] * periods, index=range(periods))
    })
    
    # Create dummy cash flow
    cash_flow = pd.DataFrame({
        'ending_cash': pd.Series([0.0] * periods, index=range(periods))
    })
    
    # Create dummy income statement
    income_statement = pd.DataFrame({
        'ebitda': pnl['ebitda']
    })
    
    kpis = calculate_kpis(
        income_statement,
        cash_flow,
        loan_schedule,
        pnl_statement=pnl,
        opex_df=None,
        owner_comp_config=None,
        time_mode='monthly'
    )
    
    # Assertions
    # Gross margin = gross_profit / revenue
    expected_gross_margin = 23210.0 / 105500.0
    assert kpis['gross_margin'].iloc[0] == pytest.approx(expected_gross_margin, abs=0.001), \
        f"Gross margin should be {expected_gross_margin:.4f}, got {kpis['gross_margin'].iloc[0]:.4f}"
    
    # EBITDA margin = ebitda / revenue
    expected_ebitda_margin = 9947.67 / 105500.0
    assert kpis['ebitda_margin'].iloc[0] == pytest.approx(expected_ebitda_margin, abs=0.001), \
        f"EBITDA margin should be {expected_ebitda_margin:.4f}, got {kpis['ebitda_margin'].iloc[0]:.4f}"
    
    # Net margin = net_income / revenue
    expected_net_margin = 8456.0 / 105500.0
    assert kpis['net_margin'].iloc[0] == pytest.approx(expected_net_margin, abs=0.001), \
        f"Net margin should be {expected_net_margin:.4f}, got {kpis['net_margin'].iloc[0]:.4f}"
    
    print(f"✅ TEST A PASSED: Margins calculated correctly")
    print(f"   Gross Margin: {kpis['gross_margin'].iloc[0]:.4f} (expected {expected_gross_margin:.4f})")
    print(f"   EBITDA Margin: {kpis['ebitda_margin'].iloc[0]:.4f} (expected {expected_ebitda_margin:.4f})")
    print(f"   Net Margin: {kpis['net_margin'].iloc[0]:.4f} (expected {expected_net_margin:.4f})")


def test_contribution_margin():
    """
    TEST B: Contribution margin
    
    Inputs:
    revenue = 105500
    cogs = 82290
    
    Expected:
    contribution_margin_pct ≈ 0.2200
    """
    # Setup test data
    periods = 12
    revenue = pd.Series([105500.0] * periods, index=range(periods))
    cogs = pd.Series([82290.0] * periods, index=range(periods))
    
    # Calculate contribution margin
    contrib_margin = calculate_contribution_margin(revenue, cogs)
    
    # Assertions
    expected_contrib_margin = (105500.0 - 82290.0) / 105500.0
    assert contrib_margin.iloc[0] == pytest.approx(expected_contrib_margin, abs=0.001), \
        f"Contribution margin should be {expected_contrib_margin:.4f}, got {contrib_margin.iloc[0]:.4f}"
    
    print(f"✅ TEST B PASSED: Contribution margin = {contrib_margin.iloc[0]:.4f} (expected {expected_contrib_margin:.4f})")


def test_break_even_revenue():
    """
    TEST C: Break-even revenue
    
    Inputs:
    payroll = 4088.3333333333335
    operating_expenses = 9174
    fixed_costs = 13262.333333333334
    contribution_margin_pct = 0.22
    
    Expected:
    break_even_revenue ≈ 60283
    """
    # Setup test data
    payroll = 4088.3333333333335
    operating_expenses = 9174.0
    fixed_costs = payroll + operating_expenses
    contribution_margin_pct = 0.22
    
    # Calculate break-even revenue
    break_even = calculate_break_even_revenue(
        indirect_payroll=payroll * 12,  # Annualize
        fixed_opex=operating_expenses * 12,  # Annualize
        semi_fixed_opex=0.0,
        owner_salary_annual=0.0,
        annual_debt_service=0.0,
        contribution_margin_pct=contribution_margin_pct,
        time_mode='monthly'
    )
    
    # Assertions
    expected_break_even = fixed_costs * 12 / contribution_margin_pct
    assert break_even == pytest.approx(expected_break_even, abs=100), \
        f"Break-even revenue should be {expected_break_even:.0f}, got {break_even:.0f}"
    
    # Monthly break-even
    monthly_break_even = break_even / 12
    expected_monthly = fixed_costs / contribution_margin_pct
    assert monthly_break_even == pytest.approx(expected_monthly, abs=10), \
        f"Monthly break-even should be {expected_monthly:.0f}, got {monthly_break_even:.0f}"
    
    print(f"✅ TEST C PASSED: Break-even revenue")
    print(f"   Annual: ${break_even:,.0f} (expected ${expected_break_even:,.0f})")
    print(f"   Monthly: ${monthly_break_even:,.0f} (expected ${expected_monthly:,.0f})")


def test_working_capital_sign_behavior():
    """
    TEST D: Working capital sign behavior
    
    If:
    prior_ar = 10000
    current_ar = 12000
    ar_change = 2000
    
    Then:
    cash impact = -2000 (AR increase is use of cash)
    
    If:
    prior_ap = 15000
    current_ap = 17000
    ap_change = 2000
    
    Then:
    cash impact = +2000 (AP increase is source of cash)
    
    If:
    prior_inventory = 5000
    current_inventory = 6500
    inventory_change = 1500
    
    Then:
    cash impact = -1500 (Inventory increase is use of cash)
    """
    from sbi_hub.modules.financial_modeler.engine.statements import build_cash_flow_statement
    
    # Setup test data
    periods = 2
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    revenue_total = pd.Series([50000.0, 50000.0], index=range(periods))
    cogs = pd.Series([20000.0, 20000.0], index=range(periods))
    
    # Build cash flow with specific AR/AP/Inventory changes
    cash_flow = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=30,
        ap_days=30,
        inventory_days=45,
        revenue_total=revenue_total,
        cogs=cogs,
        time_mode='monthly',
        owner_distribution=None,
        business_stage='existing',
        starting_ar_balance=10000.0,
        starting_ap_balance=15000.0,
        starting_inventory_balance=5000.0,
        capital_stack_enabled=False,
        beginning_cash=0.0
    )
    
    # Test AR change sign
    # Period 0: AR goes from 10000 to target (50000 * 30/30 = 50000)
    # ar_change = 50000 - 10000 = 40000 (increase)
    # Cash impact should be negative (use of cash)
    ar_change_period_0 = cash_flow['ar_change'].iloc[0]
    assert ar_change_period_0 > 0, "AR change should be positive (increase)"
    
    # In operating cash flow: net_income - ar_change
    # So positive AR change reduces cash (correct sign)
    
    # Test AP change sign
    # Period 0: AP goes from 15000 to target (20000 * 30/30 = 20000)
    # ap_change = 20000 - 15000 = 5000 (increase)
    # Cash impact should be positive (source of cash)
    ap_change_period_0 = cash_flow['ap_change'].iloc[0]
    assert ap_change_period_0 > 0, "AP change should be positive (increase)"
    
    # In operating cash flow: net_income + ap_change
    # So positive AP change increases cash (correct sign)
    
    # Test Inventory change sign
    # Period 0: Inventory goes from 5000 to target (20000 * 45/30 = 30000)
    # inventory_change = 30000 - 5000 = 25000 (increase)
    # Cash impact should be negative (use of cash)
    inventory_change_period_0 = cash_flow['inventory_change'].iloc[0]
    assert inventory_change_period_0 > 0, "Inventory change should be positive (increase)"
    
    # In operating cash flow: net_income - inventory_change
    # So positive inventory change reduces cash (correct sign)
    
    # Verify operating cash flow formula
    expected_ocf = (
        net_income.iloc[0] -
        ar_change_period_0 +
        ap_change_period_0 -
        inventory_change_period_0
    )
    actual_ocf = cash_flow['operating_cash_flow'].iloc[0]
    
    assert actual_ocf == pytest.approx(expected_ocf, abs=0.01), \
        f"Operating cash flow should be {expected_ocf:.2f}, got {actual_ocf:.2f}"
    
    print("✅ TEST D PASSED: Working capital sign behavior correct")
    print(f"   AR increase: {ar_change_period_0:,.0f} → reduces cash")
    print(f"   AP increase: {ap_change_period_0:,.0f} → increases cash")
    print(f"   Inventory increase: {inventory_change_period_0:,.0f} → reduces cash")
    print(f"   Operating Cash Flow: ${actual_ocf:,.2f}")


def test_zero_revenue_margin_safety():
    """
    TEST: Margins should be 0.0 when revenue is 0
    
    Expected:
    - All margins return 0.0 when revenue is 0
    - No division by zero errors
    """
    # Setup test data with zero revenue
    periods = 1
    revenue = pd.Series([0.0], index=range(periods))
    cogs_materials = pd.Series([0.0], index=range(periods))
    direct_payroll = pd.Series([0.0], index=range(periods))
    indirect_payroll = pd.Series([1000.0], index=range(periods))
    opex_total = pd.Series([500.0], index=range(periods))
    interest_expense = pd.Series([100.0], index=range(periods))
    
    # Build PNL statement
    pnl = build_pnl_statement(
        revenue,
        cogs_materials,
        direct_payroll,
        indirect_payroll,
        opex_total,
        interest_expense,
        annual_depreciation=0.0,
        tax_rate=0.0,
        time_mode='monthly',
        periods=periods
    )
    
    # Create dummy loan schedule
    loan_schedule = pd.DataFrame({
        'payment': pd.Series([100.0], index=range(periods)),
        'principal': pd.Series([0.0], index=range(periods)),
        'interest': pd.Series([100.0], index=range(periods))
    })
    
    # Create dummy cash flow
    cash_flow = pd.DataFrame({
        'ending_cash': pd.Series([0.0], index=range(periods))
    })
    
    # Create dummy income statement
    income_statement = pd.DataFrame({
        'ebitda': pnl['ebitda']
    })
    
    kpis = calculate_kpis(
        income_statement,
        cash_flow,
        loan_schedule,
        pnl_statement=pnl,
        opex_df=None,
        owner_comp_config=None,
        time_mode='monthly'
    )
    
    # Assertions - all margins should be 0.0
    assert kpis['gross_margin'].iloc[0] == 0.0, "Gross margin should be 0.0 when revenue is 0"
    assert kpis['ebitda_margin'].iloc[0] == 0.0, "EBITDA margin should be 0.0 when revenue is 0"
    assert kpis['net_margin'].iloc[0] == 0.0, "Net margin should be 0.0 when revenue is 0"
    
    print("✅ TEST PASSED: Zero revenue handled safely - all margins = 0.0")


if __name__ == '__main__':
    # Run all tests
    test_safe_divide()
    test_calculate_margin()
    test_margin_calculations()
    test_contribution_margin()
    test_break_even_revenue()
    test_working_capital_sign_behavior()
    test_zero_revenue_margin_safety()
    
    print("\n" + "="*70)
    print("✅ ALL METRICS ENGINE FIX TESTS PASSED")
    print("="*70)
