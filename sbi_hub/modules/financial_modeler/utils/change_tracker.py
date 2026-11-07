"""
Change tracking utility for marking unsaved changes.

Provides a simple callback function that can be used with Streamlit input widgets
to automatically mark when the model has unsaved changes.
"""

import streamlit as st


def mark_changes():
    """
    Callback function to mark that the model has unsaved changes.
    
    Use this as the on_change callback for any input widget that modifies model data.
    
    Example:
        st.number_input("Price", value=100, on_change=mark_changes)
    """
    from datetime import datetime
    from sbi_hub.modules.financial_modeler.utils.session_manager import mark_unsaved_changes
    
    # Mark unsaved changes
    mark_unsaved_changes()
    
    # Update last modified timestamp
    st.session_state['last_modified'] = datetime.now()
