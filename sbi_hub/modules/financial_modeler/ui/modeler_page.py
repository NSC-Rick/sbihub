"""
Modeler page - Non-destructive simulation layer.

Allows temporary simulation of revenue and expense adjustments.
This is an overlay-only system that does NOT modify the core model engine.
Uses ONLY pre-computed summary metrics from Review page.
"""

import streamlit as st
import streamlit.components.v1 as components
from sbi_hub.modules.financial_modeler.utils.change_tracker import mark_changes


def render():
    """Render the modeler page with simulation controls."""
    st.title("🎯 Modeler")
    
    st.markdown("---")
    
    st.subheader("Welcome to the Business Modeler")
    
    st.caption(
        "A quick overview explaining how the model works and how to interpret the results."
    )
    
    with st.expander("🎬 Watch the 2-minute Modeler introduction", expanded=False):
        video_url = "https://drive.google.com/file/d/1-HBZbPMn7jBdKJ73A6GXUXNQdYrAW84e/preview"
        
        components.iframe(
            video_url,
            height=420,
            scrolling=False
        )
    
    st.markdown("---")
    
    st.markdown("""
    Simulate revenue and expense adjustments without modifying your base model.
    All changes are temporary and reset when you reload the page.
    """)
    
    st.divider()
    
    # Check if base model has been built in Review page
    if 'review_summary_metrics' not in st.session_state:
        st.warning("⚠️ **Please build model in Review tab first.**")
        st.info("""
        The Modeler uses pre-computed summary metrics from the Review page.
        
        **Steps:**
        1. Navigate to the **Review** page
        2. Build your financial model
        3. Return to this page to run simulations
        """)
        return
    
    # Get base case metrics from session_state
    base_metrics = st.session_state.review_summary_metrics
    
    base_revenue = base_metrics['year1_revenue']
    base_operating_expenses = base_metrics['year1_operating_expenses']
    base_net_income = base_metrics['year1_net_income']
    base_debt_service = base_metrics['year1_debt_service']
    base_cash_flow = base_metrics['year1_cash_flow']
    base_dscr = base_metrics['year1_dscr']
    
    # ========================================
    # ADJUSTMENT CONTROLS
    # ========================================
    st.markdown("### Adjustment Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.modeler_revenue_adj = st.slider(
            "Revenue Adjustment",
            min_value=-30.0,
            max_value=30.0,
            value=st.session_state.modeler_revenue_adj,
            step=1.0,
            format="%.0f%%",
            help="Adjust revenue up or down by percentage",
            key="modeler_revenue_slider",
            on_change=mark_changes
        )
    
    with col2:
        st.session_state.modeler_expense_adj = st.slider(
            "Expense Adjustment",
            min_value=-30.0,
            max_value=30.0,
            value=st.session_state.modeler_expense_adj,
            step=1.0,
            format="%.0f%%",
            help="Adjust operating expenses up or down by percentage",
            key="modeler_expense_slider",
            on_change=mark_changes
        )
    
    # Scope toggle (for display only - Year 1 metrics already computed)
    st.session_state.modeler_scope = st.radio(
        "Apply Adjustment To:",
        options=["Year 1 Only", "Entire Forecast"],
        index=0 if st.session_state.modeler_scope == "Year 1 Only" else 1,
        horizontal=True,
        help="Year 1 Only: adjustments apply to Year 1 metrics. Entire Forecast: conceptual (Year 1 metrics shown)",
        key="modeler_scope_radio",
        on_change=mark_changes
    )
    
    st.divider()
    
    # ========================================
    # SIMPLIFIED ADJUSTMENT LOGIC
    # ========================================
    
    # Calculate adjusted revenue
    adj_revenue = base_revenue * (1 + st.session_state.modeler_revenue_adj / 100)
    
    # Calculate expense delta
    expense_delta = base_operating_expenses * (st.session_state.modeler_expense_adj / 100)
    
    # Calculate adjusted net income
    # Net income changes by:
    # + (adjusted revenue - base revenue) [revenue impact]
    # - expense delta [expense impact]
    revenue_impact = adj_revenue - base_revenue
    adj_net_income = base_net_income + revenue_impact - expense_delta
    
    # Calculate adjusted cash flow
    # Cash flow changes by same amount as net income
    net_income_delta = adj_net_income - base_net_income
    adj_cash_flow = base_cash_flow + net_income_delta
    
    # Calculate adjusted DSCR
    # DSCR = (EBITDA + adjustments) / debt service
    # EBITDA changes by revenue impact - expense delta
    if base_debt_service > 0 and base_dscr is not None:
        ebitda_delta = revenue_impact - expense_delta
        adj_ebitda = (base_dscr * base_debt_service) + ebitda_delta  # Back-calculate base EBITDA, then adjust
        adj_dscr = adj_ebitda / base_debt_service
    else:
        adj_dscr = None  # Debt-free
    
    # ========================================
    # DISPLAY: BASE CASE vs MODELED CASE
    # ========================================
    
    st.markdown("### 📊 Base Case vs Modeled Case Comparison")
    
    # Two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Base Case (Year 1)**")
        st.metric("Revenue", f"${base_revenue:,.2f}")
        st.metric("Net Income", f"${base_net_income:,.2f}")
        st.metric("Cash Flow", f"${base_cash_flow:,.2f}")
        st.metric("DSCR", "—" if base_dscr is None else f"{base_dscr:.2f}")
    
    with col2:
        st.markdown("**Modeled Case (Year 1)**")
        
        # Revenue with delta
        rev_delta = adj_revenue - base_revenue
        st.metric("Revenue", f"${adj_revenue:,.2f}", delta=f"${rev_delta:,.2f}")
        
        # Net Income with delta
        ni_delta = adj_net_income - base_net_income
        st.metric("Net Income", f"${adj_net_income:,.2f}", delta=f"${ni_delta:,.2f}")
        
        # Cash Flow with delta
        cf_delta = adj_cash_flow - base_cash_flow
        st.metric("Cash Flow", f"${adj_cash_flow:,.2f}", delta=f"${cf_delta:,.2f}")
        
        # DSCR with delta
        if adj_dscr is None:
            st.metric("DSCR", "—")
        else:
            dscr_delta = adj_dscr - base_dscr if base_dscr is not None else 0
            st.metric("DSCR", f"{adj_dscr:.2f}", delta=f"{dscr_delta:+.2f}")
    
    st.divider()
    
    # ========================================
    # IMPACT SUMMARY
    # ========================================
    
    st.markdown("### Impact Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Δ Net Income**")
        if ni_delta > 0:
            st.success(f"✅ +${ni_delta:,.2f}")
        elif ni_delta < 0:
            st.error(f"⚠️ ${ni_delta:,.2f}")
        else:
            st.info(f"➖ ${ni_delta:,.2f}")
    
    with col2:
        st.markdown("**Δ Cash Flow**")
        if cf_delta > 0:
            st.success(f"✅ +${cf_delta:,.2f}")
        elif cf_delta < 0:
            st.error(f"⚠️ ${cf_delta:,.2f}")
        else:
            st.info(f"➖ ${cf_delta:,.2f}")
    
    with col3:
        st.markdown("**DSCR Status**")
        if adj_dscr is None:
            st.success(f"🟢 Debt Free")
        elif adj_dscr >= 1.25:
            st.success(f"🟢 {adj_dscr:.2f} (Strong)")
        elif adj_dscr >= 1.0:
            st.warning(f"🟡 {adj_dscr:.2f} (Marginal)")
        else:
            st.error(f"🔴 {adj_dscr:.2f} (Below 1.0)")
    
    st.divider()
    
    # Reset button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Reset to Base Case", type="secondary"):
            st.session_state.modeler_revenue_adj = 0.0
            st.session_state.modeler_expense_adj = 0.0
            st.session_state.modeler_scope = "Year 1 Only"
            st.rerun()
    
    # Info box
    st.info("""
    **Note:** These adjustments are for simulation only and do not modify your saved scenario.
    Adjustments persist during your session but reset when you reload the page.
    """)
    
    # Debug info (optional - can be removed)
    with st.expander("🔍 Debug: Base Metrics"):
        st.json(base_metrics)
