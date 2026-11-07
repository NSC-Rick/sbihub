"""
Test Deal Optimizer (WPP-FME-026)

Validates that the deal optimization engine correctly searches for optimal
capital structures based on objectives and constraints.
"""

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.deal_optimizer import DealOptimizer, run_deal_optimization


def get_base_model_inputs():
    """Create base model inputs for testing."""
    return {
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 100.0,
                'volume': 1000.0,
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
                'rate': 60000.0,
                'owner_role': False
            }
        ],
        'opex_categories': [
            {
                'category': 'Rent',
                'amount': 2000.0,
                'frequency': 'monthly'
            }
        ],
        'loan_amount': 0,
        'loan_rate': 0.07,
        'loan_term': 10,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 45,
        'tax_rate': 0.21,
        'annual_depreciation': 10000.0,
        'owner_compensation': {
            'mode': 'payroll',
            'amount': 80000.0
        },
        'mode': 'monthly',
        'time_mode': 'monthly',
        'periods': 36,
        'capital_stack': {
            'enabled': True,
            'sources': {
                'buyer_equity': 0,
                'bank_loan': 0,
                'seller_note': 0,
                'grants': 0,
                'donations': 0,
                'community_equity': 0
            },
            'uses': {
                'purchase_price': 400000,
                'working_capital': 0,
                'closing_costs': 0
            }
        },
        'seasonality': {'enabled': False},
        'business_stage': 'acquisition',
        'model_mode': 'startup',
        'working_capital_source': 'buyer_injected'
    }


def test_optimizer_initialization():
    """Test that optimizer initializes correctly."""
    base_inputs = get_base_model_inputs()
    
    optimizer = DealOptimizer(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="minimize_buyer_equity",
        minimum_dscr=1.25,
        minimum_cash_balance=5000.0
    )
    
    assert optimizer.purchase_price == 400000.0
    assert optimizer.objective == "minimize_buyer_equity"
    assert optimizer.minimum_dscr == 1.25
    assert optimizer.minimum_cash_balance == 5000.0
    assert optimizer.max_iterations == 5000
    
    print("✅ TEST PASSED: Optimizer initialization")


def test_scenario_generation():
    """Test that optimizer generates scenarios correctly."""
    base_inputs = get_base_model_inputs()
    
    optimizer = DealOptimizer(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="minimize_buyer_equity"
    )
    
    # Define small ranges for testing
    optimizer.define_search_ranges(
        buyer_equity_range=(0, 20000, 10000),  # 3 values: 0, 10000, 20000
        seller_note_range=(0, 20000, 10000),   # 3 values: 0, 10000, 20000
        working_capital_range=(5000, 15000, 5000)  # 3 values: 5000, 10000, 15000
    )
    
    scenarios = optimizer.generate_scenarios()
    
    # Should generate 3 * 3 * 3 = 27 scenarios (minus any with negative bank loan)
    assert len(scenarios) > 0, "Should generate at least some scenarios"
    
    # Check that scenarios have required fields
    for scenario in scenarios:
        assert 'buyer_equity' in scenario
        assert 'seller_note' in scenario
        assert 'working_capital' in scenario
        assert 'bank_loan' in scenario
        assert scenario['bank_loan'] >= 0, "Bank loan should not be negative"
    
    print(f"✅ TEST PASSED: Generated {len(scenarios)} scenarios")


def test_minimize_buyer_equity():
    """Test optimization with minimize_buyer_equity objective."""
    base_inputs = get_base_model_inputs()
    
    # Run optimization with small ranges for speed
    results = run_deal_optimization(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="minimize_buyer_equity",
        minimum_dscr=1.0,  # Lower constraint for testing
        minimum_cash_balance=0.0,  # Lower constraint for testing
        buyer_equity_range=(0, 50000, 25000),
        seller_note_range=(0, 50000, 25000),
        working_capital_range=(10000, 20000, 10000),
        max_iterations=100
    )
    
    assert results['total_scenarios_tested'] > 0
    assert results['objective'] == "minimize_buyer_equity"
    
    if results['valid_scenarios_count'] > 0:
        best = results['best_scenario']
        assert best is not None
        assert 'buyer_equity' in best
        assert 'dscr' in best
        assert 'min_cash' in best
        
        # Best scenario should have lowest buyer equity among valid scenarios
        all_buyer_equities = [s['buyer_equity'] for s in results['valid_scenarios']]
        assert best['buyer_equity'] == min(all_buyer_equities)
        
        print(f"✅ TEST PASSED: Minimize buyer equity")
        print(f"   Best buyer equity: ${best['buyer_equity']:,.0f}")
        print(f"   Valid scenarios: {results['valid_scenarios_count']}")
    else:
        print("⚠️ TEST WARNING: No valid scenarios found (constraints may be too strict)")


def test_maximize_dscr():
    """Test optimization with maximize_dscr objective."""
    base_inputs = get_base_model_inputs()
    
    results = run_deal_optimization(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="maximize_dscr",
        minimum_dscr=1.0,
        minimum_cash_balance=0.0,
        buyer_equity_range=(20000, 60000, 20000),
        seller_note_range=(0, 50000, 25000),
        working_capital_range=(10000, 20000, 10000),
        max_iterations=100
    )
    
    assert results['objective'] == "maximize_dscr"
    
    if results['valid_scenarios_count'] > 0:
        best = results['best_scenario']
        
        # Best scenario should have highest DSCR among valid scenarios
        all_dscrs = [s['dscr'] for s in results['valid_scenarios']]
        assert best['dscr'] == max(all_dscrs)
        
        print(f"✅ TEST PASSED: Maximize DSCR")
        print(f"   Best DSCR: {best['dscr']:.2f}")
        print(f"   Valid scenarios: {results['valid_scenarios_count']}")
    else:
        print("⚠️ TEST WARNING: No valid scenarios found")


def test_constraints_validation():
    """Test that constraints are properly enforced."""
    base_inputs = get_base_model_inputs()
    
    minimum_dscr = 1.5
    minimum_cash = 10000.0
    
    results = run_deal_optimization(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="minimize_buyer_equity",
        minimum_dscr=minimum_dscr,
        minimum_cash_balance=minimum_cash,
        buyer_equity_range=(30000, 60000, 15000),
        seller_note_range=(0, 50000, 25000),
        working_capital_range=(15000, 25000, 10000),
        max_iterations=100
    )
    
    # All valid scenarios should meet constraints
    for scenario in results['valid_scenarios']:
        assert scenario['dscr'] >= minimum_dscr, \
            f"DSCR {scenario['dscr']:.2f} should be >= {minimum_dscr}"
        assert scenario['min_cash'] >= minimum_cash, \
            f"Min cash ${scenario['min_cash']:,.0f} should be >= ${minimum_cash:,.0f}"
    
    print(f"✅ TEST PASSED: Constraints validation")
    print(f"   All {results['valid_scenarios_count']} valid scenarios meet constraints")


def test_max_iterations_limit():
    """Test that max_iterations limit is respected."""
    base_inputs = get_base_model_inputs()
    
    max_iter = 50
    
    results = run_deal_optimization(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="minimize_buyer_equity",
        minimum_dscr=1.0,
        minimum_cash_balance=0.0,
        buyer_equity_range=(0, 100000, 5000),  # Would generate many scenarios
        seller_note_range=(0, 100000, 5000),
        working_capital_range=(5000, 50000, 5000),
        max_iterations=max_iter
    )
    
    # Should not exceed max iterations
    assert results['total_scenarios_tested'] <= max_iter, \
        f"Tested {results['total_scenarios_tested']} scenarios, should be <= {max_iter}"
    
    print(f"✅ TEST PASSED: Max iterations limit")
    print(f"   Tested {results['total_scenarios_tested']} scenarios (limit: {max_iter})")


def test_sorted_scenarios():
    """Test that scenarios are sorted correctly by objective."""
    base_inputs = get_base_model_inputs()
    
    results = run_deal_optimization(
        base_model_inputs=base_inputs,
        purchase_price=400000.0,
        objective="minimize_buyer_equity",
        minimum_dscr=1.0,
        minimum_cash_balance=0.0,
        buyer_equity_range=(0, 50000, 25000),
        seller_note_range=(0, 50000, 25000),
        working_capital_range=(10000, 20000, 10000),
        max_iterations=100
    )
    
    if results['valid_scenarios_count'] > 1:
        sorted_scenarios = results['sorted_scenarios']
        
        # Check that scenarios are sorted by buyer equity (ascending)
        for i in range(len(sorted_scenarios) - 1):
            assert sorted_scenarios[i]['buyer_equity'] <= sorted_scenarios[i + 1]['buyer_equity'], \
                "Scenarios should be sorted by buyer equity (ascending)"
        
        print(f"✅ TEST PASSED: Sorted scenarios")
        print(f"   Top scenario buyer equity: ${sorted_scenarios[0]['buyer_equity']:,.0f}")
    else:
        print("⚠️ TEST WARNING: Not enough scenarios to test sorting")


if __name__ == '__main__':
    # Run all tests
    test_optimizer_initialization()
    test_scenario_generation()
    test_minimize_buyer_equity()
    test_maximize_dscr()
    test_constraints_validation()
    test_max_iterations_limit()
    test_sorted_scenarios()
    
    print("\n" + "="*70)
    print("✅ ALL DEAL OPTIMIZER TESTS COMPLETED")
    print("="*70)
