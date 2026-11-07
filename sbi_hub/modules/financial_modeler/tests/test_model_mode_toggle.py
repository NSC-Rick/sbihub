"""
Test Model Mode Toggle (WPP-FME-023)

Validates that model_mode toggle correctly handles startup vs acquisition scenarios
with proper opening working capital initialization.
"""

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.statements import calculate_opening_working_capital, build_cash_flow_statement


def test_calculate_opening_working_capital_startup():
    """
    TEST A: Startup mode
    
    Inputs:
    AR days = 10
    AP days = 30
    Inventory days = 25
    
    Expected:
    opening_ar = 0
    opening_ap = 0
    opening_inventory = 0
    """
    opening_wc = calculate_opening_working_capital(
        model_mode='startup',
        revenue_period_0=105500.0,
        cogs_period_0=82946.0,
        ar_days=10,
        ap_days=30,
        inventory_days=25,
        days_in_period=30
    )
    
    assert opening_wc['ar'] == 0.0, "Startup mode should have zero opening AR"
    assert opening_wc['ap'] == 0.0, "Startup mode should have zero opening AP"
    assert opening_wc['inventory'] == 0.0, "Startup mode should have zero opening Inventory"
    
    print("✅ TEST A PASSED: Startup mode has zero opening balances")


def test_calculate_opening_working_capital_acquisition():
    """
    TEST B: Acquisition mode
    
    Inputs:
    Revenue = 105,500
    COGS = 82,946
    AR days = 3
    AP days = 30
    Inventory days = 25
    
    Expected:
    opening_ar ≈ 10,550
    opening_ap ≈ 82,946
    opening_inventory ≈ 69,121
    """
    revenue = 105500.0
    cogs = 82946.0
    ar_days = 3
    ap_days = 30
    inventory_days = 25
    days_in_period = 30
    
    opening_wc = calculate_opening_working_capital(
        model_mode='acquisition',
        revenue_period_0=revenue,
        cogs_period_0=cogs,
        ar_days=ar_days,
        ap_days=ap_days,
        inventory_days=inventory_days,
        days_in_period=days_in_period
    )
    
    # Calculate expected values
    expected_ar = revenue * (ar_days / days_in_period)
    expected_ap = cogs * (ap_days / days_in_period)
    expected_inventory = cogs * (inventory_days / days_in_period)
    
    assert opening_wc['ar'] == pytest.approx(expected_ar, abs=1), \
        f"Opening AR should be {expected_ar:.2f}, got {opening_wc['ar']:.2f}"
    assert opening_wc['ap'] == pytest.approx(expected_ap, abs=1), \
        f"Opening AP should be {expected_ap:.2f}, got {opening_wc['ap']:.2f}"
    assert opening_wc['inventory'] == pytest.approx(expected_inventory, abs=1), \
        f"Opening Inventory should be {expected_inventory:.2f}, got {opening_wc['inventory']:.2f}"
    
    print(f"✅ TEST B PASSED: Acquisition mode calculates opening balances")
    print(f"   Opening AR: ${opening_wc['ar']:,.2f} (expected ${expected_ar:,.2f})")
    print(f"   Opening AP: ${opening_wc['ap']:,.2f} (expected ${expected_ap:,.2f})")
    print(f"   Opening Inventory: ${opening_wc['inventory']:,.2f} (expected ${expected_inventory:,.2f})")


def test_startup_mode_no_period_1_spike():
    """
    TEST: Startup mode should not create artificial spike in Period 1
    
    Expected:
    - Period 0: Working capital builds from zero
    - Period 1: Only normal changes based on revenue/COGS changes
    - No artificial spike
    """
    periods = 3
    revenue = pd.Series([105500.0, 110000.0, 115000.0], index=range(periods))
    cogs = pd.Series([82946.0, 86500.0, 90000.0], index=range(periods))
    net_income = pd.Series([10000.0, 11000.0, 12000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0, 0.0], index=range(periods))
    
    cash_flow = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=10,
        ap_days=30,
        inventory_days=25,
        revenue_total=revenue,
        cogs=cogs,
        time_mode='monthly',
        owner_distribution=None,
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0,
        model_mode='startup'
    )
    
    # In startup mode, Period 0 should build working capital from zero
    # Period 1 should only have normal changes
    ar_change_period_0 = cash_flow['ar_change'].iloc[0]
    ar_change_period_1 = cash_flow['ar_change'].iloc[1]
    
    # Period 0 AR change should be positive (building from zero)
    assert ar_change_period_0 > 0, "Period 0 should build AR from zero"
    
    # Period 1 AR change should be smaller (only revenue growth)
    # Not a huge spike from opening balance initialization
    assert abs(ar_change_period_1) < abs(ar_change_period_0), \
        "Period 1 AR change should be smaller than Period 0 (no spike)"
    
    print("✅ TEST PASSED: Startup mode - no Period 1 spike")
    print(f"   Period 0 AR change: ${ar_change_period_0:,.2f}")
    print(f"   Period 1 AR change: ${ar_change_period_1:,.2f}")


def test_acquisition_mode_minimal_period_1_change():
    """
    TEST: Acquisition mode should have minimal Period 1 changes
    
    Expected:
    - Period 0: Opening balances already set from operating assumptions
    - Period 1: Only small changes based on revenue/COGS changes
    - No artificial spike
    """
    periods = 3
    revenue = pd.Series([105500.0, 110000.0, 115000.0], index=range(periods))
    cogs = pd.Series([82946.0, 86500.0, 90000.0], index=range(periods))
    net_income = pd.Series([10000.0, 11000.0, 12000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0, 0.0], index=range(periods))
    
    cash_flow = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=10,
        ap_days=30,
        inventory_days=25,
        revenue_total=revenue,
        cogs=cogs,
        time_mode='monthly',
        owner_distribution=None,
        business_stage='acquisition',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0,
        model_mode='acquisition',
        working_capital_source='seller_provided'  # Use seller_provided to get acquisition-like behavior
    )
    
    # In acquisition mode, Period 0 should have small changes
    # (opening balances already match operating assumptions)
    ar_change_period_0 = cash_flow['ar_change'].iloc[0]
    ar_change_period_1 = cash_flow['ar_change'].iloc[1]
    
    # Period 0 AR change should be small (opening already set correctly)
    # Period 1 AR change should also be small (only revenue growth)
    assert abs(ar_change_period_0) < 2000, \
        f"Period 0 AR change should be small in acquisition mode, got ${ar_change_period_0:,.2f}"
    
    assert abs(ar_change_period_1) < 2000, \
        f"Period 1 AR change should be small in acquisition mode, got ${ar_change_period_1:,.2f}"
    
    print("✅ TEST PASSED: Acquisition mode - minimal Period 0 and Period 1 changes")
    print(f"   Period 0 AR change: ${ar_change_period_0:,.2f}")
    print(f"   Period 1 AR change: ${ar_change_period_1:,.2f}")


def test_startup_vs_acquisition_comparison():
    """
    TEST: Compare startup vs acquisition mode side-by-side
    
    Expected:
    - Startup: Large Period 0 working capital build
    - Acquisition: Small Period 0 working capital changes
    """
    periods = 2
    revenue = pd.Series([105500.0, 105500.0], index=range(periods))
    cogs = pd.Series([82946.0, 82946.0], index=range(periods))
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    
    # Build startup mode cash flow
    cash_flow_startup = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=30,
        ap_days=30,
        inventory_days=45,
        revenue_total=revenue,
        cogs=cogs,
        time_mode='monthly',
        owner_distribution=None,
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0,
        model_mode='startup'
    )
    
    # Build acquisition mode cash flow
    cash_flow_acquisition = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=30,
        ap_days=30,
        inventory_days=45,
        revenue_total=revenue,
        cogs=cogs,
        time_mode='monthly',
        owner_distribution=None,
        business_stage='acquisition',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0,
        model_mode='acquisition',
        working_capital_source='seller_provided'  # Use seller_provided to get acquisition-like behavior
    )
    
    # Compare Period 0 working capital changes
    startup_ar_change_p0 = cash_flow_startup['ar_change'].iloc[0]
    acquisition_ar_change_p0 = cash_flow_acquisition['ar_change'].iloc[0]
    
    startup_inventory_change_p0 = cash_flow_startup['inventory_change'].iloc[0]
    acquisition_inventory_change_p0 = cash_flow_acquisition['inventory_change'].iloc[0]
    
    # Startup should have large Period 0 changes (building from zero)
    assert abs(startup_ar_change_p0) > 50000, \
        f"Startup AR change should be large, got ${startup_ar_change_p0:,.2f}"
    
    assert abs(startup_inventory_change_p0) > 100000, \
        f"Startup Inventory change should be large, got ${startup_inventory_change_p0:,.2f}"
    
    # Acquisition should have small Period 0 changes (already initialized)
    assert abs(acquisition_ar_change_p0) < 1000, \
        f"Acquisition AR change should be small, got ${acquisition_ar_change_p0:,.2f}"
    
    assert abs(acquisition_inventory_change_p0) < 1000, \
        f"Acquisition Inventory change should be small, got ${acquisition_inventory_change_p0:,.2f}"
    
    print("✅ TEST PASSED: Startup vs Acquisition comparison")
    print(f"\n   STARTUP MODE (Period 0):")
    print(f"   AR change: ${startup_ar_change_p0:,.2f}")
    print(f"   Inventory change: ${startup_inventory_change_p0:,.2f}")
    print(f"\n   ACQUISITION MODE (Period 0):")
    print(f"   AR change: ${acquisition_ar_change_p0:,.2f}")
    print(f"   Inventory change: ${acquisition_inventory_change_p0:,.2f}")


def test_explicit_starting_balances_override():
    """
    TEST: Explicit starting balances should override model_mode
    
    Expected:
    - When explicit starting balances are provided, use those
    - model_mode is ignored
    """
    periods = 2
    revenue = pd.Series([105500.0, 105500.0], index=range(periods))
    cogs = pd.Series([82946.0, 82946.0], index=range(periods))
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    
    # Provide explicit starting balances
    explicit_ar = 50000.0
    explicit_ap = 30000.0
    explicit_inventory = 40000.0
    
    cash_flow = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=30,
        ap_days=30,
        inventory_days=45,
        revenue_total=revenue,
        cogs=cogs,
        time_mode='monthly',
        owner_distribution=None,
        business_stage='acquisition',
        starting_ar_balance=explicit_ar,
        starting_ap_balance=explicit_ap,
        starting_inventory_balance=explicit_inventory,
        capital_stack_enabled=False,
        beginning_cash=0.0,
        model_mode='startup'  # This should be ignored
    )
    
    # Period 0 changes should be based on explicit starting balances
    # Not on model_mode
    target_ar = revenue.iloc[0] * (30 / 30)
    expected_ar_change = target_ar - explicit_ar
    
    actual_ar_change = cash_flow['ar_change'].iloc[0]
    
    assert actual_ar_change == pytest.approx(expected_ar_change, abs=1), \
        f"AR change should be based on explicit starting balance, expected ${expected_ar_change:,.2f}, got ${actual_ar_change:,.2f}"
    
    print("✅ TEST PASSED: Explicit starting balances override model_mode")
    print(f"   Explicit AR: ${explicit_ar:,.2f}")
    print(f"   Target AR: ${target_ar:,.2f}")
    print(f"   AR change: ${actual_ar_change:,.2f}")


if __name__ == '__main__':
    # Run all tests
    test_calculate_opening_working_capital_startup()
    test_calculate_opening_working_capital_acquisition()
    test_startup_mode_no_period_1_spike()
    test_acquisition_mode_minimal_period_1_change()
    test_startup_vs_acquisition_comparison()
    test_explicit_starting_balances_override()
    
    print("\n" + "="*70)
    print("✅ ALL MODEL MODE TOGGLE TESTS PASSED")
    print("="*70)
