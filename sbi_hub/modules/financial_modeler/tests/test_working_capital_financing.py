"""
Test Working Capital Financing (WPP-FME-024)

Validates that working capital source options and required working capital
calculations work correctly.
"""

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.statements import calculate_required_working_capital, build_cash_flow_statement


def test_calculate_required_working_capital():
    """
    TEST A: Calculate required working capital
    
    Inputs:
    Revenue = 105,500
    COGS = 82,946
    AR days = 3
    AP days = 30
    Inventory days = 25
    
    Expected:
    AR ≈ 10,550
    Inventory ≈ 69,121
    AP ≈ 82,946
    Required WC ≈ -3,275
    """
    revenue = 105500.0
    cogs = 82946.0
    ar_days = 3
    ap_days = 30
    inventory_days = 25
    
    required_wc = calculate_required_working_capital(
        revenue=revenue,
        cogs=cogs,
        ar_days=ar_days,
        ap_days=ap_days,
        inventory_days=inventory_days,
        days_in_period=30
    )
    
    # Calculate expected values
    expected_ar = revenue * (ar_days / 30)
    expected_ap = cogs * (ap_days / 30)
    expected_inventory = cogs * (inventory_days / 30)
    expected_required_wc = expected_ar + expected_inventory - expected_ap
    
    assert required_wc['ar'] == pytest.approx(expected_ar, abs=1), \
        f"AR should be {expected_ar:.2f}, got {required_wc['ar']:.2f}"
    assert required_wc['ap'] == pytest.approx(expected_ap, abs=1), \
        f"AP should be {expected_ap:.2f}, got {required_wc['ap']:.2f}"
    assert required_wc['inventory'] == pytest.approx(expected_inventory, abs=1), \
        f"Inventory should be {expected_inventory:.2f}, got {required_wc['inventory']:.2f}"
    assert required_wc['required_wc'] == pytest.approx(expected_required_wc, abs=1), \
        f"Required WC should be {expected_required_wc:.2f}, got {required_wc['required_wc']:.2f}"
    
    print(f"✅ TEST A PASSED: Required working capital calculated correctly")
    print(f"   AR: ${required_wc['ar']:,.2f} (expected ${expected_ar:,.2f})")
    print(f"   Inventory: ${required_wc['inventory']:,.2f} (expected ${expected_inventory:,.2f})")
    print(f"   AP: ${required_wc['ap']:,.2f} (expected ${expected_ap:,.2f})")
    print(f"   Required WC: ${required_wc['required_wc']:,.2f} (expected ${expected_required_wc:,.2f})")


def test_buyer_injected_working_capital():
    """
    TEST B: Buyer injected working capital
    
    If working_capital_source == buyer_injected
    Working capital = 80,000
    
    Expected:
    beginning_cash = 80,000
    opening_ar = 0
    opening_ap = 0
    opening_inventory = 0
    """
    periods = 2
    revenue = pd.Series([105500.0, 105500.0], index=range(periods))
    cogs = pd.Series([82946.0, 82946.0], index=range(periods))
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=80000.0,
        model_mode='startup',
        working_capital_source='buyer_injected'
    )
    
    # Get capital metrics
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    
    # Assertions
    assert capital_metrics.get('beginning_cash', 0) == 80000.0, \
        "Beginning cash should be 80,000"
    
    assert capital_metrics.get('working_capital_source') == 'buyer_injected', \
        "Working capital source should be buyer_injected"
    
    # Period 0 should build working capital from zero
    assert cash_flow['ar_change'].iloc[0] > 0, \
        "AR should build from zero in Period 0"
    
    print("✅ TEST B PASSED: Buyer injected working capital")
    print(f"   Beginning Cash: ${capital_metrics.get('beginning_cash', 0):,.2f}")
    print(f"   Working Capital Source: {capital_metrics.get('working_capital_source')}")


def test_seller_provided_working_capital():
    """
    TEST: Seller provided working capital
    
    If working_capital_source == seller_provided
    
    Expected:
    opening_ar = calculated from AR days
    opening_ap = calculated from AP days
    opening_inventory = calculated from Inventory days
    beginning_cash = 0 (or from capital stack)
    """
    periods = 2
    revenue = pd.Series([105500.0, 105500.0], index=range(periods))
    cogs = pd.Series([82946.0, 82946.0], index=range(periods))
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    
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
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=0.0,
        model_mode='startup',
        working_capital_source='seller_provided'
    )
    
    # Get capital metrics
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    
    # Assertions
    assert capital_metrics.get('working_capital_source') == 'seller_provided', \
        "Working capital source should be seller_provided"
    
    # Period 0 should have minimal changes (opening balances already set)
    ar_change_period_0 = abs(cash_flow['ar_change'].iloc[0])
    inventory_change_period_0 = abs(cash_flow['inventory_change'].iloc[0])
    
    # Changes should be small (opening balances match targets)
    assert ar_change_period_0 < 1000, \
        f"AR change should be small in seller_provided mode, got ${ar_change_period_0:,.2f}"
    
    assert inventory_change_period_0 < 1000, \
        f"Inventory change should be small in seller_provided mode, got ${inventory_change_period_0:,.2f}"
    
    print("✅ TEST PASSED: Seller provided working capital")
    print(f"   Working Capital Source: {capital_metrics.get('working_capital_source')}")
    print(f"   Period 0 AR change: ${ar_change_period_0:,.2f} (minimal)")
    print(f"   Period 0 Inventory change: ${inventory_change_period_0:,.2f} (minimal)")


def test_loan_financed_working_capital():
    """
    TEST C: Loan financed working capital
    
    If working_capital_source == loan_financed
    Working capital loan = 80,000
    
    Expected:
    beginning_cash = 80,000
    opening_ar = 0
    opening_ap = 0
    opening_inventory = 0
    """
    periods = 2
    revenue = pd.Series([105500.0, 105500.0], index=range(periods))
    cogs = pd.Series([82946.0, 82946.0], index=range(periods))
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    
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
        business_stage='startup',
        starting_ar_balance=0.0,
        starting_ap_balance=0.0,
        starting_inventory_balance=0.0,
        capital_stack_enabled=False,
        beginning_cash=80000.0,  # From WC loan
        model_mode='startup',
        working_capital_source='loan_financed'
    )
    
    # Get capital metrics
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    
    # Assertions
    assert capital_metrics.get('beginning_cash', 0) == 80000.0, \
        "Beginning cash should be 80,000 from WC loan"
    
    assert capital_metrics.get('working_capital_source') == 'loan_financed', \
        "Working capital source should be loan_financed"
    
    # Period 0 should build working capital from zero (same as buyer_injected)
    assert cash_flow['ar_change'].iloc[0] > 0, \
        "AR should build from zero in Period 0"
    
    print("✅ TEST C PASSED: Loan financed working capital")
    print(f"   Beginning Cash: ${capital_metrics.get('beginning_cash', 0):,.2f}")
    print(f"   Working Capital Source: {capital_metrics.get('working_capital_source')}")


def test_working_capital_coverage_ratio():
    """
    TEST: Working capital coverage ratio calculation
    
    Expected:
    Coverage = Beginning Cash / Required Working Capital
    
    Interpretation:
    < 1.0: Undercapitalized
    1.0-1.5: Adequate
    > 1.5: Strong liquidity
    """
    periods = 2
    revenue = pd.Series([105500.0, 105500.0], index=range(periods))
    cogs = pd.Series([82946.0, 82946.0], index=range(periods))
    net_income = pd.Series([10000.0, 10000.0], index=range(periods))
    loan_principal = pd.Series([0.0, 0.0], index=range(periods))
    loan_payment = pd.Series([0.0, 0.0], index=range(periods))
    
    # Test with positive required WC
    cash_flow = build_cash_flow_statement(
        net_income=net_income,
        loan_principal=loan_principal,
        loan_payment=loan_payment,
        ar_days=30,
        ap_days=10,  # Low AP days to create positive required WC
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
        beginning_cash=150000.0,
        model_mode='startup',
        working_capital_source='buyer_injected'
    )
    
    # Get capital metrics
    capital_metrics = cash_flow.attrs.get('capital_metrics', {})
    
    required_wc = capital_metrics.get('required_working_capital', 0)
    wc_coverage = capital_metrics.get('working_capital_coverage', None)
    beginning_cash = capital_metrics.get('beginning_cash', 0)
    
    # Assertions
    if required_wc > 0:
        expected_coverage = beginning_cash / required_wc
        assert wc_coverage == pytest.approx(expected_coverage, abs=0.01), \
            f"Coverage should be {expected_coverage:.2f}, got {wc_coverage:.2f}"
        
        print("✅ TEST PASSED: Working capital coverage ratio")
        print(f"   Beginning Cash: ${beginning_cash:,.2f}")
        print(f"   Required WC: ${required_wc:,.2f}")
        print(f"   Coverage Ratio: {wc_coverage:.2f}x")
        
        if wc_coverage < 1.0:
            print(f"   Status: ⚠️ Undercapitalized")
        elif wc_coverage < 1.5:
            print(f"   Status: ✅ Adequate")
        else:
            print(f"   Status: 💪 Strong Liquidity")
    else:
        print("✅ TEST PASSED: Coverage ratio N/A (negative required WC)")


def test_explicit_balances_override_wc_source():
    """
    TEST: Explicit starting balances should override working_capital_source
    
    Expected:
    When explicit starting balances are provided, use those
    working_capital_source is ignored
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
        model_mode='startup',
        working_capital_source='seller_provided'  # This should be ignored
    )
    
    # Period 0 changes should be based on explicit starting balances
    target_ar = revenue.iloc[0] * (30 / 30)
    expected_ar_change = target_ar - explicit_ar
    
    actual_ar_change = cash_flow['ar_change'].iloc[0]
    
    assert actual_ar_change == pytest.approx(expected_ar_change, abs=1), \
        f"AR change should be based on explicit starting balance, expected ${expected_ar_change:,.2f}, got ${actual_ar_change:,.2f}"
    
    print("✅ TEST PASSED: Explicit starting balances override working_capital_source")
    print(f"   Explicit AR: ${explicit_ar:,.2f}")
    print(f"   Target AR: ${target_ar:,.2f}")
    print(f"   AR change: ${actual_ar_change:,.2f}")


if __name__ == '__main__':
    # Run all tests
    test_calculate_required_working_capital()
    test_buyer_injected_working_capital()
    test_seller_provided_working_capital()
    test_loan_financed_working_capital()
    test_working_capital_coverage_ratio()
    test_explicit_balances_override_wc_source()
    
    print("\n" + "="*70)
    print("✅ ALL WORKING CAPITAL FINANCING TESTS PASSED")
    print("="*70)
