"""
Test Period-0 AP Double Counting Fix (WPP-FME-019)

Validates that Period 0 AP does not create phantom liquidity in startup/acquisition scenarios.
"""

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.statements import build_cash_flow_statement


def test_startup_acquisition_no_phantom_ap():
    """
    TEST A: Startup/acquisition with capital stack enabled
    
    Expected:
    - Period 0 ap_change = 0
    - Period 0 OCF is tight/negative
    - No artificial AP liquidity
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build cash flow with startup/acquisition mode
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
        business_stage='acquisition',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=True,
        model_mode='startup'  # Use startup mode to ensure zero opening AP
    )
    
    # Assertions
    # Period 0 AP change should be ZERO (no phantom supplier credit in startup mode)
    assert cash_flow['ap_change'].iloc[0] == 0.0, \
        f"Period 0 AP change should be 0 in startup mode, got {cash_flow['ap_change'].iloc[0]}"
    
    # Period 0 AR change should be positive (increase in AR = cash outflow)
    # Note: In OCF calculation, we subtract AR change, so positive AR change reduces cash
    assert cash_flow['ar_change'].iloc[0] > 0, \
        "Period 0 AR change should be positive (AR buildup)"
    
    # Period 0 inventory change should be positive (increase in inventory = cash outflow)
    # Note: In OCF calculation, we subtract inventory change, so positive inventory change reduces cash
    assert cash_flow['inventory_change'].iloc[0] > 0, \
        "Period 0 inventory change should be positive (inventory buildup)"
    
    # Verify debug metadata
    debug = cash_flow.attrs.get('period_0_debug', {})
    assert debug['is_startup_like'] == True, "Should be detected as startup-like"
    assert debug['ap_change_period_0'] == 0.0, "Period 0 AP change should be 0 in debug"
    
    print("✅ TEST A PASSED: No phantom AP in startup/acquisition mode")


def test_existing_business_with_starting_ap():
    """
    TEST B: Existing business with starting AP entered
    
    Expected:
    - AP logic works from explicit starting balance
    - No forced zero AP behavior
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build cash flow with existing business mode and starting AP
    starting_ap = 15000.0
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
        starting_ar_balance=0.0,
        starting_ap_balance=starting_ap,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False
    )
    
    # Assertions
    # Period 0 AP change should reflect change from starting balance to target
    target_ap = 20000.0  # cogs * (ap_days / 30)
    expected_ap_change = target_ap - starting_ap
    
    assert abs(cash_flow['ap_change'].iloc[0] - expected_ap_change) < 0.01, \
        f"Period 0 AP change should be {expected_ap_change}, got {cash_flow['ap_change'].iloc[0]}"
    
    # Verify debug metadata
    debug = cash_flow.attrs.get('period_0_debug', {})
    assert debug['beginning_ap_balance'] == starting_ap, \
        f"Beginning AP should be {starting_ap}, got {debug['beginning_ap_balance']}"
    
    print("✅ TEST B PASSED: Existing business with starting AP works correctly")


def test_period_1_onward_ap_builds_normally():
    """
    TEST C: Period 1 onward
    
    Expected:
    - AP begins building normally from operations
    - Cash flow table remains stable and continuous
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build cash flow with startup mode
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
        model_mode='startup'  # Use startup mode to ensure zero opening AP
    )
    
    # Assertions
    # Period 0 AP change should be 0 in startup mode
    assert cash_flow['ap_change'].iloc[0] == 0.0, "Period 0 AP change should be 0 in startup mode"
    
    # Period 1 AP change should be positive (building AP from 0 to target)
    target_ap_period_1 = 20000.0  # cogs * (ap_days / 30)
    assert cash_flow['ap_change'].iloc[1] > 0, \
        f"Period 1 AP change should be positive, got {cash_flow['ap_change'].iloc[1]}"
    
    # Period 2+ should have minimal AP changes (stable operations)
    for period in range(2, min(6, periods)):
        # AP change should be near zero for stable revenue/cogs
        assert abs(cash_flow['ap_change'].iloc[period]) < 100, \
            f"Period {period} AP change should be near 0, got {cash_flow['ap_change'].iloc[period]}"
    
    # Verify no NaN values
    assert not cash_flow['ap_change'].isna().any(), "No NaN values in AP change"
    assert not cash_flow['ending_cash'].isna().any(), "No NaN values in ending cash"
    
    print("✅ TEST C PASSED: Period 1+ AP builds normally")


def test_acquisition_with_explicit_starting_ap():
    """
    TEST: Acquisition mode with explicit starting AP (edge case)
    
    Expected:
    - Even in acquisition mode, if starting AP is provided, use it
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build cash flow with acquisition mode BUT explicit starting AP
    starting_ap = 10000.0
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
        business_stage='acquisition',
        starting_ar_balance=0.0,
        starting_ap_balance=starting_ap,  # Explicit starting AP
        starting_inventory_balance=0.0,
        capital_stack_enabled=True
    )
    
    # Assertions
    # Period 0 AP change should NOT be zero (explicit starting balance provided)
    target_ap = 20000.0
    expected_ap_change = target_ap - starting_ap
    
    assert cash_flow['ap_change'].iloc[0] != 0.0, \
        "Period 0 AP change should not be 0 when explicit starting AP provided"
    
    assert abs(cash_flow['ap_change'].iloc[0] - expected_ap_change) < 0.01, \
        f"Period 0 AP change should be {expected_ap_change}, got {cash_flow['ap_change'].iloc[0]}"
    
    print("✅ TEST PASSED: Acquisition with explicit starting AP works correctly")


def test_working_capital_requirement_calculation():
    """
    TEST: Working capital requirement should account for zero Period 0 AP
    
    Expected:
    - WC requirement = (AR + Inventory) - AP
    - With AP = 0 in Period 0, WC requirement is higher
    - Capital metrics should calculate cash injection needed
    """
    # Setup test data
    periods = 12
    net_income = pd.Series([5000.0] * periods, index=range(periods))
    loan_principal = pd.Series([500.0] * periods, index=range(periods))
    loan_payment = pd.Series([1000.0] * periods, index=range(periods))
    revenue_total = pd.Series([50000.0] * periods, index=range(periods))
    cogs = pd.Series([20000.0] * periods, index=range(periods))
    
    # Build cash flow with startup mode
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
        model_mode='startup'  # Use startup mode to ensure zero opening AP
    )
    
    # Calculate expected WC requirement
    # AR = 50000 * (30/30) = 50000
    # Inventory = 20000 * (45/30) = 30000
    # AP = 0 (forced to zero in startup mode Period 0)
    # WC = 50000 + 30000 - 0 = 80000
    
    expected_wc = 80000.0
    period_0_debug = cash_flow.attrs.get('period_0_debug', {})
    actual_wc = period_0_debug.get('working_capital_requirement', 0)
    
    assert abs(actual_wc - expected_wc) < 0.01, \
        f"WC requirement should be {expected_wc}, got {actual_wc}"
    
    # Period 0 ending cash should be negative (no artificial injection)
    assert cash_flow['ending_cash'].iloc[0] < 0, \
        "Period 0 ending cash should be negative without startup capital"
    
    # Capital metrics should show cash injection required
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    cash_injection_required = capital_metrics.get('cash_injection_required', 0)
    
    assert cash_injection_required > 0, \
        "Cash injection should be required for startup scenario"
    
    print("✅ TEST PASSED: Working capital requirement calculated correctly with zero AP")


if __name__ == '__main__':
    # Run all tests
    test_startup_acquisition_no_phantom_ap()
    test_existing_business_with_starting_ap()
    test_period_1_onward_ap_builds_normally()
    test_acquisition_with_explicit_starting_ap()
    test_working_capital_requirement_calculation()
    
    print("\n" + "="*70)
    print("✅ ALL PERIOD-0 AP FIX TESTS PASSED")
    print("="*70)
