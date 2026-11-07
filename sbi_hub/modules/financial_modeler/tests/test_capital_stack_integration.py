"""
Test Capital Stack Integration (WPP-FME-021)

Validates that capital stack working capital correctly feeds beginning cash in the cash flow model.
"""

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.statements import build_cash_flow_statement


def test_no_capital_stack():
    """
    TEST A: No capital stack enabled
    
    Expected:
    - Beginning Cash = 0
    - Cash flow unchanged from baseline
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build cash flow with no capital stack (beginning_cash = 0)
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0
    )
    
    # Assertions
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    beginning_cash = capital_metrics.get('beginning_cash', 0)
    
    assert beginning_cash == 0.0, \
        f"Beginning cash should be 0 with no capital stack, got {beginning_cash}"
    
    # Period 0 ending cash should be negative (no funding)
    assert cash_flow['ending_cash'].iloc[0] < 0, \
        "Period 0 ending cash should be negative without capital stack funding"
    
    print("✅ TEST A PASSED: No capital stack - beginning cash = 0")


def test_working_capital_30k():
    """
    TEST B: Working capital = $30,000
    
    Expected:
    - Beginning Cash = $30,000
    - Period 0 ending cash increases by $30,000 compared to baseline
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build baseline (no capital stack)
    baseline = build_cash_flow_statement(
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0
    )
    
    # Build with $30k working capital
    working_capital = 30000.0
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=True,
        beginning_cash=working_capital
    )
    
    # Assertions
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    beginning_cash = capital_metrics.get('beginning_cash', 0)
    
    assert beginning_cash == working_capital, \
        f"Beginning cash should be {working_capital}, got {beginning_cash}"
    
    # Period 0 ending cash should increase by exactly the working capital amount
    baseline_ending = baseline['ending_cash'].iloc[0]
    funded_ending = cash_flow['ending_cash'].iloc[0]
    difference = funded_ending - baseline_ending
    
    assert abs(difference - working_capital) < 0.01, \
        f"Period 0 ending cash should increase by {working_capital}, got {difference}"
    
    print(f"✅ TEST B PASSED: Working capital $30k - ending cash increased by ${difference:,.2f}")


def test_working_capital_75k():
    """
    TEST C: Working capital = $75,000
    
    Expected:
    - Beginning Cash = $75,000
    - Period 0 ending cash increases by $75,000 compared to baseline
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build baseline (no capital stack)
    baseline = build_cash_flow_statement(
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0
    )
    
    # Build with $75k working capital
    working_capital = 75000.0
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=True,
        beginning_cash=working_capital
    )
    
    # Assertions
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    beginning_cash = capital_metrics.get('beginning_cash', 0)
    
    assert beginning_cash == working_capital, \
        f"Beginning cash should be {working_capital}, got {beginning_cash}"
    
    # Period 0 ending cash should increase by exactly the working capital amount
    baseline_ending = baseline['ending_cash'].iloc[0]
    funded_ending = cash_flow['ending_cash'].iloc[0]
    difference = funded_ending - baseline_ending
    
    assert abs(difference - working_capital) < 0.01, \
        f"Period 0 ending cash should increase by {working_capital}, got {difference}"
    
    # Verify ending cash improved significantly
    assert funded_ending > baseline_ending, \
        f"Period 0 ending cash should be higher with funding: baseline={baseline_ending}, funded={funded_ending}"
    
    print(f"✅ TEST C PASSED: Working capital $75k - ending cash = ${funded_ending:,.2f} (improved from ${baseline_ending:,.2f})")


def test_working_capital_150k():
    """
    TEST D: Working capital = $150,000
    
    Expected:
    - Beginning Cash = $150,000
    - Period 0 ending cash increases by $150,000 compared to baseline
    - Substantial positive cash position
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build baseline (no capital stack)
    baseline = build_cash_flow_statement(
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0
    )
    
    # Build with $150k working capital
    working_capital = 150000.0
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=True,
        beginning_cash=working_capital
    )
    
    # Assertions
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    beginning_cash = capital_metrics.get('beginning_cash', 0)
    
    assert beginning_cash == working_capital, \
        f"Beginning cash should be {working_capital}, got {beginning_cash}"
    
    # Period 0 ending cash should increase by exactly the working capital amount
    baseline_ending = baseline['ending_cash'].iloc[0]
    funded_ending = cash_flow['ending_cash'].iloc[0]
    difference = funded_ending - baseline_ending
    
    assert abs(difference - working_capital) < 0.01, \
        f"Period 0 ending cash should increase by {working_capital}, got {difference}"
    
    # With $150k, ending cash should be substantially positive
    assert funded_ending > 50000, \
        f"Period 0 ending cash should be substantially positive with $150k funding, got {funded_ending}"
    
    print(f"✅ TEST D PASSED: Working capital $150k - ending cash = ${funded_ending:,.2f}")


def test_no_double_counting():
    """
    TEST: Confirm no double counting
    
    Expected:
    - working_capital_injection row NOT present in DataFrame
    - Capital stack working capital only affects beginning cash
    - No additional artificial funding in later periods
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build with working capital
    working_capital = 75000.0
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=True,
        beginning_cash=working_capital
    )
    
    # Assertions
    # 1. No working_capital_injection column
    assert 'working_capital_injection' not in cash_flow.columns, \
        "working_capital_injection row should NOT be present in cash flow DataFrame"
    
    # 2. Net cash flow should be pure (no artificial injections)
    # Verify: net_cash_flow = operating_cash_flow + financing_cash_flow - owner_distribution
    for period in range(periods):
        expected_net_cash = (
            cash_flow['operating_cash_flow'].iloc[period] +
            cash_flow['financing_cash_flow'].iloc[period] -
            cash_flow['owner_distribution'].iloc[period]
        )
        actual_net_cash = cash_flow['net_cash_flow'].iloc[period]
        
        assert abs(expected_net_cash - actual_net_cash) < 0.01, \
            f"Period {period}: Net cash flow should be pure, expected {expected_net_cash}, got {actual_net_cash}"
    
    # 3. Ending cash follows cumulative pattern
    # ending_cash[i] = beginning_cash + sum(net_cash_flow[0:i+1])
    cumulative_net_cash = cash_flow['net_cash_flow'].cumsum()
    for period in range(periods):
        expected_ending = working_capital + cumulative_net_cash.iloc[period]
        actual_ending = cash_flow['ending_cash'].iloc[period]
        
        assert abs(expected_ending - actual_ending) < 0.01, \
            f"Period {period}: Ending cash should follow cumulative pattern, expected {expected_ending}, got {actual_ending}"
    
    print("✅ TEST PASSED: No double counting - capital stack only affects beginning cash")


def test_capital_requirement_metrics_with_funding():
    """
    TEST: Capital requirement metrics should account for beginning cash
    
    Expected:
    - If beginning_cash covers the deficit, cash_injection_required should be 0
    - Break-even period should be earlier with funding
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build without funding
    no_funding = build_cash_flow_statement(
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0
    )
    
    # Build with sufficient funding
    working_capital = 100000.0
    with_funding = build_cash_flow_statement(
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=True,
        beginning_cash=working_capital
    )
    
    # Get capital metrics
    no_funding_metrics = no_funding.attrs.get('capital_metrics', {})
    with_funding_metrics = with_funding.attrs.get('capital_metrics', {})
    
    # Assertions
    # Without funding, cash injection should be required
    assert no_funding_metrics['cash_injection_required'] > 0, \
        "Without funding, cash injection should be required"
    
    # With sufficient funding, no additional cash injection should be required
    assert with_funding_metrics['cash_injection_required'] == 0, \
        f"With sufficient funding, no additional cash injection should be required, got {with_funding_metrics['cash_injection_required']}"
    
    # Break-even should occur earlier (or immediately) with funding
    no_funding_breakeven = no_funding_metrics['break_even_period']
    with_funding_breakeven = with_funding_metrics['break_even_period']
    
    if with_funding_breakeven is not None and no_funding_breakeven is not None:
        assert with_funding_breakeven <= no_funding_breakeven, \
            f"Break-even should occur earlier with funding: without={no_funding_breakeven}, with={with_funding_breakeven}"
    
    print(f"✅ TEST PASSED: Capital metrics correctly account for beginning cash funding")


if __name__ == '__main__':
    # Run all tests
    test_no_capital_stack()
    test_working_capital_30k()
    test_working_capital_75k()
    test_working_capital_150k()
    test_no_double_counting()
    test_capital_requirement_metrics_with_funding()
    
    print("\n" + "="*70)
    print("✅ ALL CAPITAL STACK INTEGRATION TESTS PASSED")
    print("="*70)
