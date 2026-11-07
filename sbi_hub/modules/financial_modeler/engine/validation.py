import json
from typing import Dict, Any, Tuple


def get_default_model_inputs():
    """
    Get default model inputs structure.
    
    Returns:
        Dict with all default model parameters
    """
    return {
        'time_mode': 'monthly',
        'periods': 36,  # Default: 3 years × 12 months
        'revenue_streams': [
            {
                'name': 'Product Sales',
                'price': 100.0,
                'volume': 100.0,
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
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15,
                'role_type': 'indirect'
            }
        ],
        'opex_items': [
            {'name': 'Rent', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Utilities', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Heat', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Insurance', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Maintenance', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Subscriptions', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Professional Fees', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Marketing', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Office / Supplies', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'},
            {'name': 'Miscellaneous', 'amount': 0.0, 'growth_rate': 0.03, 'category': 'fixed'}
        ],
        'loan_principal': 50000.0,
        'loan_annual_rate': 0.06,
        'loan_term_months': 60,
        'loan_start_period': 0,
        # Dual loan structure (Advanced mode)
        'business_loan_amount': 0.0,
        'business_interest_rate': 0.06,
        'business_amort_years': 5,
        'real_estate_loan_amount': 0.0,
        'real_estate_interest_rate': 0.06,
        'real_estate_amort_years': 10,
        'ar_days': 30,
        'ap_days': 30,
        'inventory_days': 30,
        'tax_rate': 0.25,
        'annual_depreciation': 0.0,
        'owner_compensation': {
            'mode': 'distribution',
            'amount': 0.0
        },
        'capital_stack': {
            'enabled': False,
            'uses': {
                # Legacy fields (preserved for backward compatibility)
                'purchase_price': 0.0,
                'closing_costs': 0.0,
                # New Business Acquisition fields
                'business_purchase_price': 0.0,
                'inventory_adjustment': 0.0,
                'business_closing_costs': 0.0,
                # New Real Estate fields
                'real_estate_purchase': 0.0,
                'real_estate_closing_costs': 0.0,
                # Other uses
                'working_capital': 0.0,
                'capex': 0.0
            },
            'sources': {
                'buyer_equity': 0.0,
                'community_equity': 0.0,
                'donations': 0.0,
                'bank_loan': {
                    'amount': 0.0,
                    'rate': 0.06,
                    'term': 10
                },
                'seller_note': {
                    'amount': 0.0,
                    'rate': 0.05,
                    'term': 5
                }
            }
        },
        'mode': 'Basic',
        'seasonality': {
            'enabled': False,
            'mode': 'OFF',
            'custom_weights': [8.33] * 12
        },
        'revenue_input_method': 'Monthly Revenue Target',
        'monthly_revenue': 0.0,
        'avg_sale': 25.0,
        'monthly_transactions': 0.0,
        'customers_per_day': 0.0,
        'days_open': 30.0
    }


def validate_scenario_json(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate scenario JSON structure.
    
    Args:
        data: Parsed JSON data
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Scenario must be a JSON object"
    
    required_keys = [
        'time_mode',
        'periods',
        'revenue_streams',
        'global_cogs_pct',
        'payroll_roles',
        'opex_items',
        'loan_principal',
        'loan_annual_rate',
        'loan_term_months',
        'loan_start_period',
        'ar_days',
        'ap_days',
        'inventory_days',
        'tax_rate',
        'annual_depreciation'
    ]
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    if data['time_mode'] not in ['monthly', 'annual']:
        return False, "time_mode must be 'monthly' or 'annual'"
    
    if not isinstance(data['revenue_streams'], list):
        return False, "revenue_streams must be a list"
    
    if not isinstance(data['payroll_roles'], list):
        return False, "payroll_roles must be a list"
    
    if not isinstance(data['opex_items'], list):
        return False, "opex_items must be a list"
    
    for i, stream in enumerate(data['revenue_streams']):
        if not isinstance(stream, dict):
            return False, f"revenue_streams[{i}] must be an object"
        required_stream_keys = ['name', 'price', 'volume', 'growth_rate']
        missing = [k for k in required_stream_keys if k not in stream]
        if missing:
            return False, f"revenue_streams[{i}] missing keys: {', '.join(missing)}"
    
    for i, role in enumerate(data['payroll_roles']):
        if not isinstance(role, dict):
            return False, f"payroll_roles[{i}] must be an object"
        required_role_keys = ['role', 'headcount', 'pay_type', 'rate', 'annual_raise_pct', 'payroll_tax_pct', 'benefits_pct']
        missing = [k for k in required_role_keys if k not in role]
        if missing:
            return False, f"payroll_roles[{i}] missing keys: {', '.join(missing)}"
    
    for i, item in enumerate(data['opex_items']):
        if not isinstance(item, dict):
            return False, f"opex_items[{i}] must be an object"
        required_item_keys = ['name', 'amount', 'growth_rate']
        missing = [k for k in required_item_keys if k not in item]
        if missing:
            return False, f"opex_items[{i}] missing keys: {', '.join(missing)}"
    
    return True, ""


def session_state_to_model_inputs(session_state) -> Dict[str, Any]:
    """
    Convert Streamlit session state to model_inputs dictionary.
    
    Args:
        session_state: Streamlit session state object
    
    Returns:
        Dict with all model inputs
    """
    return {
        'time_mode': session_state.get('time_mode', 'monthly'),
        'periods': session_state.get('periods', 36),  # Default: 3 years × 12 months
        'revenue_streams': session_state.get('revenue_streams', []),
        'global_cogs_pct': session_state.get('global_cogs_pct', 0.30),
        'cogs_improvement_pct': session_state.get('cogs_improvement_pct', 0.0),
        'startup_ramp_months': session_state.get('startup_ramp_months', 0),
        'payroll_roles': session_state.get('payroll_roles', []),
        'opex_items': session_state.get('opex_items', []),
        'loan_principal': session_state.get('loan_principal', 0.0),
        'loan_annual_rate': session_state.get('loan_annual_rate', 0.0),
        'loan_term_months': session_state.get('loan_term_months', 60),
        'loan_start_period': session_state.get('loan_start_period', 0),
        # Dual loan structure (Advanced mode)
        'business_loan_amount': session_state.get('business_loan_amount', 0.0),
        'business_interest_rate': session_state.get('business_interest_rate', 0.06),
        'business_amort_years': session_state.get('business_amort_years', 5),
        'real_estate_loan_amount': session_state.get('real_estate_loan_amount', 0.0),
        'real_estate_interest_rate': session_state.get('real_estate_interest_rate', 0.06),
        'real_estate_amort_years': session_state.get('real_estate_amort_years', 10),
        'ar_days': session_state.get('ar_days', 30),
        'ap_days': session_state.get('ap_days', 30),
        'inventory_days': session_state.get('inventory_days', 30),
        'tax_rate': session_state.get('tax_rate', 0.25),
        'annual_depreciation': session_state.get('annual_depreciation', 0.0),
        'owner_compensation': session_state.get('owner_compensation', {'mode': 'distribution', 'amount': 0.0}),
        'capital_stack': session_state.get('capital_stack', {
            'enabled': False,
            'uses': {
                'purchase_price': 0.0,
                'closing_costs': 0.0,
                'business_purchase_price': 0.0,
                'inventory_adjustment': 0.0,
                'business_closing_costs': 0.0,
                'real_estate_purchase': 0.0,
                'real_estate_closing_costs': 0.0,
                'working_capital': 0.0,
                'capex': 0.0
            },
            'sources': {
                'buyer_equity': 0.0,
                'community_equity': 0.0,
                'donations': 0.0,
                'bank_loan': {'amount': 0.0, 'rate': 0.06, 'term': 10},
                'seller_note': {'amount': 0.0, 'rate': 0.05, 'term': 5}
            }
        }),
        'mode': session_state.get('mode', 'Basic'),
        'seasonality': session_state.get('seasonality', {
            'enabled': False,
            'mode': 'OFF',
            'custom_weights': [8.33] * 12
        }),
        'revenue_input_method': session_state.get('revenue_input_method', 'Monthly Revenue Target'),
        'monthly_revenue': session_state.get('monthly_revenue', 0.0),
        'avg_sale': session_state.get('avg_sale', 25.0),
        'monthly_transactions': session_state.get('monthly_transactions', 0.0),
        'customers_per_day': session_state.get('customers_per_day', 0.0),
        'days_open': session_state.get('days_open', 30.0)
    }


def model_inputs_to_session_state(model_inputs: Dict[str, Any], session_state):
    """
    Load model_inputs dictionary into Streamlit session state.
    
    Args:
        model_inputs: Dict with all model inputs
        session_state: Streamlit session state object
    """
    session_state.time_mode = model_inputs['time_mode']
    session_state.periods = model_inputs['periods']
    session_state.revenue_streams = model_inputs['revenue_streams']
    session_state.global_cogs_pct = model_inputs['global_cogs_pct']
    session_state.cogs_improvement_pct = model_inputs.get('cogs_improvement_pct', 0.0)
    session_state.startup_ramp_months = model_inputs.get('startup_ramp_months', 0)
    session_state.payroll_roles = model_inputs['payroll_roles']
    session_state.opex_items = model_inputs['opex_items']
    session_state.loan_principal = model_inputs['loan_principal']
    session_state.loan_annual_rate = model_inputs['loan_annual_rate']
    session_state.loan_term_months = model_inputs['loan_term_months']
    session_state.loan_start_period = model_inputs['loan_start_period']
    
    # Dual loan structure (Advanced mode)
    session_state.business_loan_amount = model_inputs.get('business_loan_amount', 0.0)
    session_state.business_interest_rate = model_inputs.get('business_interest_rate', 0.06)
    session_state.business_amort_years = model_inputs.get('business_amort_years', 5)
    session_state.real_estate_loan_amount = model_inputs.get('real_estate_loan_amount', 0.0)
    session_state.real_estate_interest_rate = model_inputs.get('real_estate_interest_rate', 0.06)
    session_state.real_estate_amort_years = model_inputs.get('real_estate_amort_years', 10)
    
    # Backward compatibility migration: map legacy loan_principal to business_loan_amount
    if session_state.loan_principal > 0 and session_state.business_loan_amount == 0.0:
        session_state.business_loan_amount = session_state.loan_principal
        session_state.business_interest_rate = session_state.loan_annual_rate
        session_state.business_amort_years = session_state.loan_term_months / 12
    
    session_state.ar_days = model_inputs['ar_days']
    session_state.ap_days = model_inputs['ap_days']
    session_state.inventory_days = model_inputs['inventory_days']
    session_state.tax_rate = model_inputs['tax_rate']
    session_state.annual_depreciation = model_inputs['annual_depreciation']
    session_state.owner_compensation = model_inputs.get('owner_compensation', {'mode': 'distribution', 'amount': 0.0})
    capital_stack = model_inputs.get('capital_stack', {
        'enabled': False,
        'uses': {
            'purchase_price': 0.0,
            'closing_costs': 0.0,
            'business_purchase_price': 0.0,
            'inventory_adjustment': 0.0,
            'business_closing_costs': 0.0,
            'real_estate_purchase': 0.0,
            'real_estate_closing_costs': 0.0,
            'working_capital': 0.0,
            'capex': 0.0
        },
        'sources': {
            'buyer_equity': 0.0,
            'community_equity': 0.0,
            'donations': 0.0,
            'bank_loan': {'amount': 0.0, 'rate': 0.06, 'term': 10},
            'seller_note': {'amount': 0.0, 'rate': 0.05, 'term': 5}
        }
    })
    
    # Backward compatibility migration: convert legacy purchase_price to new structure
    uses = capital_stack.get('uses', {})
    if 'purchase_price' in uses and uses.get('purchase_price', 0.0) > 0:
        if 'business_purchase_price' not in uses or uses.get('business_purchase_price', 0.0) == 0.0:
            # Migrate legacy purchase_price to business_purchase_price
            capital_stack['uses']['business_purchase_price'] = uses['purchase_price']
            capital_stack['uses']['real_estate_purchase'] = 0.0
    
    # Ensure all new fields exist with defaults
    if 'business_purchase_price' not in uses:
        capital_stack['uses']['business_purchase_price'] = 0.0
    if 'business_closing_costs' not in uses:
        capital_stack['uses']['business_closing_costs'] = 0.0
    if 'real_estate_purchase' not in uses:
        capital_stack['uses']['real_estate_purchase'] = 0.0
    if 'real_estate_closing_costs' not in uses:
        capital_stack['uses']['real_estate_closing_costs'] = 0.0
    
    session_state.capital_stack = capital_stack
    session_state.mode = model_inputs.get('mode', 'Basic')
    session_state.seasonality = model_inputs.get('seasonality', {
        'enabled': False,
        'mode': 'OFF',
        'custom_weights': [8.33] * 12
    })
    session_state.revenue_input_method = model_inputs.get('revenue_input_method', 'Monthly Revenue Target')
    session_state.monthly_revenue = model_inputs.get('monthly_revenue', 0.0)
    session_state.avg_sale = model_inputs.get('avg_sale', 25.0)
    session_state.monthly_transactions = model_inputs.get('monthly_transactions', 0.0)
    session_state.customers_per_day = model_inputs.get('customers_per_day', 0.0)
    session_state.days_open = model_inputs.get('days_open', 30.0)
