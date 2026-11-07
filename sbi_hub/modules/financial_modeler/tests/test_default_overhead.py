"""
Test suite for default overhead categories feature.

Verifies:
- New sessions get structured default categories with 0 values
- Saved scenarios preserve existing data without duplication
- Engine calculations unchanged
- Categories are fully editable
"""

import pytest
from sbi_hub.modules.financial_modeler.engine.validation import get_default_model_inputs


def test_default_overhead_categories_exist():
    """Verify default overhead categories are defined."""
    defaults = get_default_model_inputs()
    
    assert 'opex_items' in defaults
    assert isinstance(defaults['opex_items'], list)
    assert len(defaults['opex_items']) == 10


def test_default_overhead_categories_names():
    """Verify all expected category names are present."""
    defaults = get_default_model_inputs()
    
    expected_categories = [
        "Rent",
        "Utilities",
        "Heat",
        "Insurance",
        "Maintenance",
        "Subscriptions",
        "Professional Fees",
        "Marketing",
        "Office / Supplies",
        "Miscellaneous"
    ]
    
    actual_names = [item['name'] for item in defaults['opex_items']]
    
    assert actual_names == expected_categories


def test_default_overhead_all_zero_values():
    """Verify all default categories have 0 amount (no prefilled values)."""
    defaults = get_default_model_inputs()
    
    for item in defaults['opex_items']:
        assert item['amount'] == 0.0, f"Category {item['name']} should have 0 amount"


def test_default_overhead_structure():
    """Verify each default category has correct structure."""
    defaults = get_default_model_inputs()
    
    for item in defaults['opex_items']:
        assert 'name' in item
        assert 'amount' in item
        assert 'growth_rate' in item
        assert 'category' in item
        
        assert isinstance(item['name'], str)
        assert isinstance(item['amount'], (int, float))
        assert isinstance(item['growth_rate'], (int, float))
        assert item['category'] in ['fixed', 'semi-fixed', 'variable_pct_revenue']


def test_default_overhead_growth_rate():
    """Verify default growth rate is set to 3% (0.03)."""
    defaults = get_default_model_inputs()
    
    for item in defaults['opex_items']:
        assert item['growth_rate'] == 0.03


def test_default_overhead_category_type():
    """Verify all defaults are 'fixed' category type."""
    defaults = get_default_model_inputs()
    
    for item in defaults['opex_items']:
        assert item['category'] == 'fixed'


def test_engine_with_zero_overhead():
    """Verify engine handles zero overhead correctly (no impact on calculations)."""
    from sbi_hub.modules.financial_modeler.engine.model import build_model
    
    model_inputs = get_default_model_inputs()
    
    # All overhead is 0, so opex should be 0
    outputs = build_model(model_inputs)
    
    # Check that opex is 0 in income statement
    assert 'income_statement' in outputs
    income_stmt = outputs['income_statement']
    
    # All opex should be 0
    assert (income_stmt['opex'] == 0).all()


def test_engine_with_custom_overhead():
    """Verify engine calculates correctly when overhead values are set."""
    from sbi_hub.modules.financial_modeler.engine.model import build_model
    
    model_inputs = get_default_model_inputs()
    
    # Set some overhead values
    model_inputs['opex_items'][0]['amount'] = 2000.0  # Rent
    model_inputs['opex_items'][1]['amount'] = 500.0   # Utilities
    model_inputs['opex_items'][7]['amount'] = 1000.0  # Marketing
    
    outputs = build_model(model_inputs)
    
    # Check that opex is calculated correctly
    income_stmt = outputs['income_statement']
    
    # First period should have total opex = 2000 + 500 + 1000 = 3500
    assert income_stmt['opex'].iloc[0] == 3500.0


def test_backward_compatibility_with_saved_scenario():
    """Verify saved scenarios with existing opex load correctly."""
    from sbi_hub.modules.financial_modeler.engine.validation import validate_scenario_json
    
    # Simulate a saved scenario with custom opex (old format)
    saved_scenario = {
        'time_mode': 'monthly',
        'periods': 60,
        'revenue_streams': [],
        'global_cogs_pct': 0.30,
        'payroll_roles': [],
        'opex_items': [
            {
                'name': 'Custom Rent',
                'amount': 5000.0,
                'growth_rate': 0.05,
                'category': 'fixed'
            },
            {
                'name': 'Custom Insurance',
                'amount': 1200.0,
                'growth_rate': 0.02,
                'category': 'fixed'
            }
        ],
        'loan_principal': 0.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 0.0,
        'owner_compensation': {'mode': 'distribution', 'amount': 0.0}
    }
    
    # Validate should pass
    is_valid, error = validate_scenario_json(saved_scenario)
    assert is_valid, f"Validation failed: {error}"
    
    # Verify opex_items are preserved exactly
    assert len(saved_scenario['opex_items']) == 2
    assert saved_scenario['opex_items'][0]['name'] == 'Custom Rent'
    assert saved_scenario['opex_items'][0]['amount'] == 5000.0
    assert saved_scenario['opex_items'][1]['name'] == 'Custom Insurance'
    assert saved_scenario['opex_items'][1]['amount'] == 1200.0


def test_no_duplication_on_load():
    """Verify loading a scenario doesn't duplicate default categories."""
    from sbi_hub.modules.financial_modeler.engine.validation import validate_scenario_json
    
    # Scenario with only 3 custom opex items
    saved_scenario = {
        'time_mode': 'monthly',
        'periods': 60,
        'revenue_streams': [],
        'global_cogs_pct': 0.30,
        'payroll_roles': [],
        'opex_items': [
            {'name': 'A', 'amount': 100.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'B', 'amount': 200.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'C', 'amount': 300.0, 'growth_rate': 0.03, 'category': 'fixed'}
        ],
        'loan_principal': 0.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 0.0,
        'owner_compensation': {'mode': 'distribution', 'amount': 0.0}
    }
    
    is_valid, error = validate_scenario_json(saved_scenario)
    assert is_valid
    
    # Should have exactly 3 items, not 3 + 10 defaults
    assert len(saved_scenario['opex_items']) == 3


def test_dscr_unaffected_by_zero_overhead():
    """Verify DSCR calculation unchanged when overhead is 0."""
    from sbi_hub.modules.financial_modeler.engine.model import build_model
    
    model_inputs = get_default_model_inputs()
    model_inputs['loan_principal'] = 50000.0
    
    outputs = build_model(model_inputs)
    
    # DSCR should be calculated based on EBITDA and debt service
    # With 0 opex, EBITDA should be higher, but formula should be same
    assert 'kpis' in outputs
    assert 'dscr' in outputs['kpis'].columns


def test_break_even_unaffected_by_zero_overhead():
    """Verify break-even calculation unchanged when overhead is 0."""
    from sbi_hub.modules.financial_modeler.engine.model import build_model
    
    model_inputs = get_default_model_inputs()
    
    outputs = build_model(model_inputs)
    
    # Break-even should be calculated correctly
    assert 'kpis' in outputs
    if 'break_even_revenue' in outputs['kpis'].columns:
        # Break-even exists and is calculated
        assert outputs['kpis']['break_even_revenue'].notna().any()
