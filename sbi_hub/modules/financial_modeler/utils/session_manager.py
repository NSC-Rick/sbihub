"""
Session management utility for autosave and restore functionality.

Uses Streamlit's session state and file-based persistence.
Provides automatic session backup and restore capabilities.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
from sbi_hub.modules.financial_modeler.config.version import PLATFORM_VERSION


# Session file location (in user's temp directory)
SESSION_FILE = Path.home() / ".finlite_session.json"


def get_session_data_for_storage():
    """
    Extract session state data that should be persisted.
    
    Returns dict with:
    - business_name: str
    - timestamp: str (ISO format)
    - app_version: str
    - model_data: dict (all model inputs)
    """
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


def save_session():
    """
    Save current session state to local file.
    Returns True if successful, False otherwise.
    """
    try:
        session_data = get_session_data_for_storage()
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Update session state tracking
        st.session_state['last_saved_timestamp'] = datetime.now()
        st.session_state['has_unsaved_changes'] = False
        
        return True
    except Exception as e:
        st.error(f"Failed to save session: {e}")
        return False


def mark_unsaved_changes():
    """
    Mark that the model has unsaved changes.
    Call this whenever user makes a change to model inputs.
    """
    st.session_state['has_unsaved_changes'] = True


def has_unsaved_changes():
    """
    Check if there are unsaved changes.
    
    Returns:
        bool: True if there are unsaved changes, False otherwise
    """
    return st.session_state.get('has_unsaved_changes', False)


def get_last_saved_timestamp():
    """
    Get the last saved timestamp.
    
    Returns:
        datetime or None: Last saved timestamp, or None if never saved
    """
    return st.session_state.get('last_saved_timestamp', None)


def load_session():
    """
    Load session data from local file.
    Returns dict or None if no session exists.
    """
    try:
        if not SESSION_FILE.exists():
            return None
        
        with open(SESSION_FILE, 'r') as f:
            session_data = json.load(f)
        
        return session_data
    except Exception as e:
        st.warning(f"Failed to load session: {e}")
        return None


def restore_session_data(session_data):
    """
    Restore session state from saved session data.
    
    Args:
        session_data: dict with 'model_data' key containing all session variables
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not session_data or 'model_data' not in session_data:
        return False
    
    try:
        model_data = session_data['model_data']
        
        # Restore all model data to session state
        for key, value in model_data.items():
            st.session_state[key] = value
        
        # Set flags to indicate session was restored
        st.session_state['session_restored'] = True
        st.session_state['session_restore_timestamp'] = session_data.get('timestamp', 'Unknown')
        st.session_state['session_restore_business'] = session_data.get('business_name', 'Unknown')
        
        # Automatically clear unsaved changes flag (restore is a save action)
        st.session_state['has_unsaved_changes'] = False
        st.session_state['last_saved'] = datetime.now()
        
        return True
    except Exception as e:
        st.error(f"Failed to restore session: {e}")
        return False


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
            
            timestamp_formatted = timestamp.strftime("%Y-%m-%d %I:%M %p")
        else:
            time_display = "Unknown"
            timestamp_formatted = "Unknown"
        
        return {
            'business_name': session_data.get('business_name', 'Untitled Business'),
            'timestamp': timestamp_str,
            'timestamp_formatted': timestamp_formatted,
            'time_display': time_display,
            'app_version': session_data.get('app_version', 'Unknown'),
            'has_data': bool(session_data.get('model_data'))
        }
    except Exception as e:
        return {
            'business_name': 'Unknown',
            'timestamp': 'Unknown',
            'timestamp_formatted': 'Unknown',
            'time_display': 'Unknown',
            'app_version': 'Unknown',
            'has_data': False,
            'error': str(e)
        }


def clear_saved_session():
    """
    Clear saved session file.
    Returns True if successful, False otherwise.
    """
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
        return True
    except Exception as e:
        st.error(f"Failed to clear session: {e}")
        return False


def autosave_session():
    """
    Automatically save session in the background.
    Call this after significant user actions.
    """
    # Only autosave if user has made changes (not on initial load)
    if 'session_initialized' in st.session_state:
        save_session()


def check_and_prompt_restore():
    """
    Check for saved session and prompt user to restore.
    Should be called early in app initialization.
    
    Returns:
        bool: True if user chose to restore, False otherwise
    """
    # Skip if already handled this session
    if 'restore_prompt_shown' in st.session_state:
        return st.session_state.get('session_restored', False)
    
    # Check for saved session
    saved_session = load_session()
    
    if not saved_session:
        st.session_state['restore_prompt_shown'] = True
        return False
    
    # Get session summary
    summary = get_session_summary(saved_session)
    
    if not summary or not summary['has_data']:
        st.session_state['restore_prompt_shown'] = True
        return False
    
    # Show restore prompt
    st.info("🔄 **Previous Session Detected**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        **Business:** {summary['business_name']}  
        **Last Modified:** {summary['time_display']} ({summary['timestamp_formatted']})  
        **Version:** {summary['app_version']}
        """)
    
    with col2:
        st.write("")  # Spacing
    
    col_restore, col_fresh = st.columns(2)
    
    with col_restore:
        if st.button("🔄 Restore Session", type="primary", use_container_width=True):
            if restore_session_data(saved_session):
                st.session_state['restore_prompt_shown'] = True
                st.success(f"✅ Session restored: {summary['business_name']}")
                st.rerun()
            return True
    
    with col_fresh:
        if st.button("🆕 Start Fresh", use_container_width=True):
            clear_saved_session()
            st.session_state['restore_prompt_shown'] = True
            st.session_state['session_restored'] = False
            st.rerun()
            return False
    
    # Stop execution until user makes a choice
    st.stop()
