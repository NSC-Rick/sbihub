"""
Financial Modeler module entry point for the SBI Hub shell.

This module wraps the existing Financial Modeler application so it can be
rendered inside the SBI Hub module router. Page configuration is owned by
the hub shell (sbi_hub), so ``st.set_page_config`` is intentionally not
called here. All application logic, screens, calculations, reports, and
workflows are preserved unchanged from the standalone deployment.
"""
import streamlit as st
import streamlit.components.v1 as components
from sbi_hub.modules.financial_modeler.ui import home, revenue_page, payroll_page, opex_page, financing_page, review_page, insights_page, modeler_page, optimizer_page
from sbi_hub.modules.financial_modeler.comparison import workspace as comparison_workspace
from sbi_hub.modules.financial_modeler.utils.session_manager import check_and_prompt_restore, autosave_session, has_unsaved_changes
from sbi_hub.modules.financial_modeler.utils.custom_styles import apply_custom_styles
from sbi_hub.modules.financial_modeler.components.elevenlabs_widget import render_elevenlabs_widget


def initialize_session_state():
    """
    Global session state initialization (WPP-SESSION-INIT-001, WPP-SESSION-INIT-002).
    Ensures core session state variables are initialized before page routing.
    """
    defaults = {
        # scenario
        "scenario_name": "Business Scenario",

        # model inputs
        "revenue_streams": [],
        "payroll_roles": [],
        "opex_categories": [],
        "financing_sources": [],
        "model_inputs": {},

        # forecast
        "forecast_periods": 36,

        # deal parameters
        "purchase_price": 0.0,

        # financing inputs
        "loan_amount": 0.0,
        "loan_rate": 0.06,
        "loan_term_years": 10,

        # optimizer
        "optimizer_results": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render():
    """Render the Financial Modeler application inside the SBI Hub shell."""
    # Apply custom styles for improved readability (Enhancement 3)
    apply_custom_styles()

    # Check for saved session and prompt restore BEFORE initialization
    check_and_prompt_restore()

    # Initialize session state before page routing
    initialize_session_state()

    # Mark session as initialized (for autosave)
    st.session_state['session_initialized'] = True

    # V2.1: Model Comparison workspace mode. Read-only with respect to the
    # active model — all model session keys are preserved on return.
    if st.session_state.get('fm_workspace') == 'comparison':
        comparison_workspace.render()
        render_elevenlabs_widget("agent_9601kwzaq0jsfrhb0xzvzaxa0hx0")
        return

    st.sidebar.title("Financial Modeler")

    pages = {
        "🏠 Home": home,
        "💵 Revenue": revenue_page,
        "👥 Payroll": payroll_page,
        "📋 Operating Expenses": opex_page,
        "🏦 Financing": financing_page,
        "📊 Review": review_page,
        "💡 Insights": insights_page,
        "🎯 Modeler": modeler_page,
        "📊 Optimization": optimizer_page
    }

    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Track page changes and scroll to top on navigation
    if 'previous_page' not in st.session_state:
        st.session_state.previous_page = selection

    if st.session_state.previous_page != selection:
        st.session_state.previous_page = selection
        st.session_state['_scroll_to_top'] = True
        # Trigger rerun to execute scroll-to-top component
        st.rerun()

    st.sidebar.divider()

    # V2.1: entry point to the Model Comparison workspace
    if st.sidebar.button(
        "⚖️ Compare Models",
        use_container_width=True,
        help="Open the Model Comparison workspace to compare your current "
             "model with a saved model, or two saved models. Your active "
             "model is preserved.",
    ):
        st.session_state['fm_workspace'] = 'comparison'
        st.session_state['_scroll_to_top'] = True
        st.rerun()

    st.sidebar.divider()

    # Model Info - Dynamic session data
    model_name = st.session_state.get('scenario_name', 'Business Scenario')
    periods = st.session_state.get('periods', 36)
    time_mode = st.session_state.get('time_mode', 'monthly')
    forecast_years = periods // 12 if time_mode == 'monthly' else periods

    st.sidebar.markdown("""
### Model Info
- **Model Name:** {name}
- **Forecast Length:** {years} Years
- **Periods:** {periods}
- **Revenue Streams:** {rev_count}
- **Payroll Roles:** {payroll_count}
- **Opex Items:** {opex_count}
""".format(
        name=model_name,
        years=forecast_years,
        periods=periods,
        rev_count=len(st.session_state.get('revenue_streams', [])),
        payroll_count=len(st.session_state.get('payroll_roles', [])),
        opex_count=len(st.session_state.get('opex_items', []))
    ))

    # Save status and last saved timestamp
    if has_unsaved_changes():
        st.sidebar.warning("🟡 **Unsaved Changes**")
    else:
        st.sidebar.success("🟢 **Saved**")

        # Show last saved timestamp if available
        from sbi_hub.modules.financial_modeler.utils.session_manager import get_last_saved_timestamp
        from datetime import datetime
        last_saved = get_last_saved_timestamp()
        if last_saved:
            time_ago = datetime.now() - last_saved
            if time_ago.seconds < 60:
                time_str = "Just now"
            elif time_ago.seconds < 3600:
                minutes = time_ago.seconds // 60
                time_str = f"{minutes} min ago"
            else:
                hours = time_ago.seconds // 3600
                time_str = f"{hours} hr ago"
            st.sidebar.caption(f"Last saved: {time_str}")

    page = pages[selection]
    page.render()

    # Scroll to top if flag is set (after page navigation or restore/load/reset)
    if st.session_state.get('_scroll_to_top', False):
        # Initialize scroll counter if not present
        if '_scroll_counter' not in st.session_state:
            st.session_state['_scroll_counter'] = 0

        # Increment counter to force component re-execution
        st.session_state['_scroll_counter'] += 1
        st.session_state['_scroll_to_top'] = False

        # Use st.components.v1.html with changing content to force re-execution
        # The counter in HTML ensures the component re-renders each time
        components.html(
            f"""
                <p style="display: none;">{st.session_state['_scroll_counter']}</p>
                <script>
                    window.parent.document.querySelector('section.main').scrollTo(0, 0);
                </script>
            """,
            height=0
        )

    # ElevenLabs Conversational AI Widget (Eric - AI Financial Coach)
    render_elevenlabs_widget("agent_9601kwzaq0jsfrhb0xzvzaxa0hx0")
