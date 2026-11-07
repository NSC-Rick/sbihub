"""
Session storage utility for browser-based session persistence.

Uses Streamlit's JavaScript bridge to interact with browser localStorage.
Provides autosave and restore capabilities for model state.
"""

import json
import streamlit as st
from datetime import datetime
from sbi_hub.modules.financial_modeler.config.version import PLATFORM_VERSION


def get_storage_key():
    """Get the localStorage key for session data."""
    return "finlite_last_session"


def get_session_data_for_storage():
    """
    Extract session state data that should be persisted.
    
    Returns dict with:
    - business_name: str
    - timestamp: str (ISO format)
    - app_version: str
    - model_data: dict (all model inputs)
    """
    # Get business name from scenario_name or default
    business_name = st.session_state.get('scenario_name', 'Untitled Business')
    
    # Collect all model-related session state
    model_data = {
        'scenario_name': st.session_state.get('scenario_name', 'Business Scenario'),
        'time_mode': st.session_state.get('time_mode', 'monthly'),
        'periods': st.session_state.get('periods', 36),
        'revenue_streams': st.session_state.get('revenue_streams', []),
        'global_cogs_pct': st.session_state.get('global_cogs_pct', 0.30),
        'cogs_improvement_pct': st.session_state.get('cogs_improvement_pct', 0.0),
        'payroll_roles': st.session_state.get('payroll_roles', []),
        'opex_items': st.session_state.get('opex_items', []),
        'loan_principal': st.session_state.get('loan_principal', 50000.0),
        'loan_annual_rate': st.session_state.get('loan_annual_rate', 0.06),
        'loan_term_months': st.session_state.get('loan_term_months', 60),
        'mode': st.session_state.get('mode', 'Basic'),
        'financing_sources': st.session_state.get('financing_sources', []),
        'purchase_price': st.session_state.get('purchase_price', 0.0),
        'inventory_adjustment': st.session_state.get('inventory_adjustment', 0.0),
        'closing_costs': st.session_state.get('closing_costs', 0.0),
        'working_capital': st.session_state.get('working_capital', 0.0),
        'capex': st.session_state.get('capex', 0.0),
        'owner_compensation_mode': st.session_state.get('owner_compensation_mode', 'payroll'),
        'owner_compensation_annual': st.session_state.get('owner_compensation_annual', 0.0),
        'ar_days': st.session_state.get('ar_days', 0),
        'ap_days': st.session_state.get('ap_days', 0),
        'inventory_days': st.session_state.get('inventory_days', 0),
        'seasonality': st.session_state.get('seasonality', {
            'mode': 'OFF',
            'enabled': False,
            'custom_weights': [8.33] * 12
        }),
        'revenue_input_method': st.session_state.get('revenue_input_method', 'Monthly Revenue Target'),
        'monthly_revenue': st.session_state.get('monthly_revenue', 10000.0),
        'avg_sale': st.session_state.get('avg_sale', 50.0),
        'monthly_transactions': st.session_state.get('monthly_transactions', 200.0),
        'customers_per_day': st.session_state.get('customers_per_day', 10.0),
        'days_open': st.session_state.get('days_open', 20.0),
        'startup_ramp_months': st.session_state.get('startup_ramp_months', 0),
        'modeler_scope': st.session_state.get('modeler_scope', 'Full Forecast'),
    }
    
    session_data = {
        'business_name': business_name,
        'timestamp': datetime.now().isoformat(),
        'app_version': PLATFORM_VERSION,
        'model_data': model_data
    }
    
    return session_data


def save_session_to_browser():
    """
    Save current session state to browser localStorage.
    Uses Streamlit's JavaScript bridge via st.components.html.
    """
    session_data = get_session_data_for_storage()
    json_data = json.dumps(session_data)
    
    # JavaScript to save to localStorage
    js_code = f"""
    <script>
        try {{
            localStorage.setItem('{get_storage_key()}', {json.dumps(json_data)});
            console.log('Session saved to localStorage');
        }} catch (e) {{
            console.error('Failed to save session:', e);
        }}
    </script>
    """
    
    # Execute JavaScript (hidden iframe)
    st.components.v1.html(js_code, height=0)


def load_session_from_browser():
    """
    Load session data from browser localStorage.
    Returns dict or None if no session exists.
    
    Note: This requires JavaScript execution and callback handling.
    Use check_for_saved_session() for the full restore flow.
    """
    # This is a placeholder - actual implementation requires
    # bidirectional communication which Streamlit doesn't support directly
    # We'll use a different approach with query params or session state flags
    pass


def restore_session_data(session_data):
    """
    Restore session state from saved session data.
    
    Args:
        session_data: dict with 'model_data' key containing all session variables
    """
    if not session_data or 'model_data' not in session_data:
        return False
    
    model_data = session_data['model_data']
    
    # Restore all model data to session state
    for key, value in model_data.items():
        st.session_state[key] = value
    
    # Set flag to indicate session was restored
    st.session_state['session_restored'] = True
    st.session_state['session_restore_timestamp'] = session_data.get('timestamp', 'Unknown')
    
    return True


def get_session_summary(session_data):
    """
    Get a human-readable summary of saved session data.
    
    Returns:
        dict with summary information for display
    """
    if not session_data:
        return None
    
    try:
        timestamp_str = session_data.get('timestamp', 'Unknown')
        if timestamp_str != 'Unknown':
            timestamp = datetime.fromisoformat(timestamp_str)
            time_ago = datetime.now() - timestamp
            
            if time_ago.days > 0:
                time_display = f"{time_ago.days} day{'s' if time_ago.days != 1 else ''} ago"
            elif time_ago.seconds > 3600:
                hours = time_ago.seconds // 3600
                time_display = f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif time_ago.seconds > 60:
                minutes = time_ago.seconds // 60
                time_display = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                time_display = "Just now"
        else:
            time_display = "Unknown"
        
        return {
            'business_name': session_data.get('business_name', 'Untitled Business'),
            'timestamp': timestamp_str,
            'time_display': time_display,
            'app_version': session_data.get('app_version', 'Unknown'),
            'has_data': bool(session_data.get('model_data'))
        }
    except Exception as e:
        return {
            'business_name': 'Unknown',
            'timestamp': 'Unknown',
            'time_display': 'Unknown',
            'app_version': 'Unknown',
            'has_data': False,
            'error': str(e)
        }


def clear_saved_session():
    """Clear saved session from browser localStorage."""
    js_code = f"""
    <script>
        try {{
            localStorage.removeItem('{get_storage_key()}');
            console.log('Session cleared from localStorage');
        }} catch (e) {{
            console.error('Failed to clear session:', e);
        }}
    </script>
    """
    
    st.components.v1.html(js_code, height=0)
