"""
Insights page with deterministic Red/Yellow/Green flags.

Rule-based analysis with transparent thresholds.
No AI commentary, no subjective language, no composite scoring.
"""

import streamlit as st
from sbi_hub.modules.financial_modeler.engine.model import build_model
from sbi_hub.modules.financial_modeler.engine.validation import session_state_to_model_inputs
from sbi_hub.modules.financial_modeler.analysis.financial_metrics import compute_financial_metrics, get_cash_metrics_for_period


def render():
    """Render the insights page with rule-based flags."""
    st.title("📊 Insights & Flags")
    
    st.markdown("""
    Deterministic analysis based on transparent rules and thresholds.
    Flags are calculated from your financial model data.
    """)
    
    st.divider()
    
    # Build model to get outputs
    model_inputs = session_state_to_model_inputs(st.session_state)
    
    try:
        with st.spinner("Analyzing model..."):
            outputs = build_model(model_inputs)
        
        # Extract key metrics
        kpis = outputs['kpis']
        income_statement = outputs['income_statement']
        cash_flow_statement = outputs['cash_flow_statement']
        loan_schedule = outputs['loan_schedule']
        
        # Compute canonical financial metrics (single source of truth)
        owner_comp_config = model_inputs.get('owner_compensation', {'mode': 'distribution', 'amount': 0.0})
        metrics = compute_financial_metrics(
            income_statement,
            cash_flow_statement,
            loan_schedule,
            owner_comp_config,
            model_inputs['time_mode']
        )
        
        # Get first period metrics from canonical source
        dscr = metrics['current_dscr']  # None if debt-free
        total_debt_service = metrics['total_debt_service']
        
        # Get cash metrics for first period
        cash_metrics = get_cash_metrics_for_period(metrics, period_index=0)
        operating_cash_flow = cash_metrics['operating_cash_flow']
        cash_after_debt = cash_metrics['cash_after_debt']
        cash_after_debt_and_owner = cash_metrics['cash_after_owner']
        
        # Get gross margin from KPIs
        first_period_kpis = kpis.iloc[0]
        gross_margin_pct = first_period_kpis.get('gross_margin_pct', 0) / 100  # Convert to decimal
        
        # Revenue for ratio calculations (annual)
        time_mode = model_inputs.get('time_mode', 'monthly')
        if time_mode == 'monthly':
            annual_revenue = income_statement['revenue'].iloc[:12].sum()
        else:
            annual_revenue = income_statement['revenue'].iloc[0]
        
        # Rent calculation (find rent in opex_items and annualize)
        monthly_rent = 0
        for item in model_inputs.get('opex_items', []):
            if item.get('name', '').lower() == 'rent':
                monthly_rent = item.get('amount', 0)
                break
        
        annual_rent = monthly_rent * 12
        rent_to_revenue_ratio = annual_rent / annual_revenue if annual_revenue > 0 else 0
        
        # Advanced mode checks
        mode = model_inputs.get('mode', 'Basic')
        is_advanced = (mode == 'Advanced')
        
        # Funding gap (Advanced only)
        funding_gap = 0
        total_uses = 0
        total_sources = 0
        if is_advanced:
            capital_stack = model_inputs.get('capital_stack', {})
            if capital_stack.get('enabled', False):
                uses = capital_stack.get('uses', {})
                sources = capital_stack.get('sources', {})
                
                # Fix double counting: use purchase_price OR business_purchase_price, not both
                purchase_price = uses.get('purchase_price', 0)
                if purchase_price > 0:
                    total_uses += purchase_price
                else:
                    total_uses += uses.get('business_purchase_price', 0)
                
                # Add other uses
                total_uses += uses.get('inventory_adjustment', 0)
                total_uses += uses.get('working_capital', 0)
                total_uses += uses.get('capex', 0)
                total_uses += uses.get('closing_costs', 0)
                total_uses += uses.get('business_closing_costs', 0)
                total_uses += uses.get('real_estate_purchase', 0)
                total_uses += uses.get('real_estate_closing_costs', 0)
                
                # Calculate sources
                total_sources = (
                    sources.get('buyer_equity', 0)
                    + sources.get('community_equity', 0)
                    + sources.get('donations', 0)
                )
                
                if 'bank_loan' in sources:
                    bank_loan = sources['bank_loan']
                    if isinstance(bank_loan, dict):
                        total_sources += bank_loan.get('amount', 0)
                    else:
                        total_sources += bank_loan
                
                if 'seller_note' in sources:
                    seller_note = sources['seller_note']
                    if isinstance(seller_note, dict):
                        total_sources += seller_note.get('amount', 0)
                    else:
                        total_sources += seller_note
                
                funding_gap = total_sources - total_uses
        
        # AR days (Advanced only)
        ar_days = model_inputs.get('ar_days', 0)
        
        # Equity injection ratio (Advanced only)
        equity_ratio = 0
        if is_advanced and total_uses > 0:
            capital_stack = model_inputs.get('capital_stack', {})
            if capital_stack.get('enabled', False):
                sources = capital_stack.get('sources', {})
                
                total_equity = (
                    sources.get('buyer_equity', 0)
                    + sources.get('community_equity', 0)
                    + sources.get('donations', 0)
                )
                
                equity_ratio = total_equity / total_uses if total_uses > 0 else 0
        
        # ========================================
        # RED FLAGS
        # ========================================
        red_flags = []
        
        # Rule: DSCR < 1.0 (only if debt exists)
        if total_debt_service > 0 and dscr is not None and dscr < 1.0:
            red_flags.append(f"DSCR below 1.0 (current: {dscr:.2f}). Debt service exceeds available cash flow.")
        
        # Rule: Cash after debt and owner < 0
        if cash_after_debt_and_owner < 0:
            red_flags.append(f"Negative cash after debt and owner compensation (${cash_after_debt_and_owner:,.2f}). Business cannot cover obligations.")
        
        # Rule: Operating cash flow < 0
        if operating_cash_flow < 0:
            red_flags.append(f"Negative operating cash flow (${operating_cash_flow:,.2f}). Operations are consuming cash.")
        
        # Rule: Advanced mode AND funding gap != 0 (with tolerance)
        if is_advanced and abs(funding_gap) > 1000:
            if funding_gap > 1000:
                red_flags.append(f"Capital stack funding surplus (${funding_gap:,.0f}). Sources exceed uses.")
            elif funding_gap < -1000:
                red_flags.append(f"Capital stack funding gap (${abs(funding_gap):,.0f}). Additional capital required.")
        
        # ========================================
        # YELLOW FLAGS
        # ========================================
        yellow_flags = []
        
        # Rule: 1.0 <= DSCR < 1.20 (only if debt exists)
        if total_debt_service > 0 and dscr is not None and 1.0 <= dscr < 1.20:
            yellow_flags.append(f"DSCR between 1.0 and 1.20 (current: {dscr:.2f}). Minimal debt service coverage.")
        
        # Rule: Rent / Revenue > 0.12
        if rent_to_revenue_ratio > 0.12:
            yellow_flags.append(f"Rent exceeds 12% of revenue (current: {rent_to_revenue_ratio*100:.1f}%). High occupancy cost.")
        
        # Rule: Gross margin < 0.30
        if gross_margin_pct < 0.30:
            yellow_flags.append(f"Gross margin below 30% (current: {gross_margin_pct*100:.1f}%). Limited pricing power or high COGS.")
        
        # Rule: Advanced mode AND AR days > 30
        if is_advanced and ar_days > 30:
            yellow_flags.append(f"Accounts receivable days exceed 30 (current: {ar_days}). Slow customer payment cycle.")
        
        # ========================================
        # GREEN SIGNALS
        # ========================================
        green_signals = []
        
        # Rule: DSCR >= 1.25 or Debt Free
        if total_debt_service == 0:
            green_signals.append(f"Debt Free. No debt service obligations.")
        elif dscr is not None and dscr >= 1.25:
            green_signals.append(f"DSCR at or above 1.25 (current: {dscr:.2f}). Strong debt service coverage.")
        
        # Rule: Cash after debt and owner >= 0
        if cash_after_debt_and_owner >= 0:
            green_signals.append(f"Positive cash after debt and owner compensation (${cash_after_debt_and_owner:,.2f}). Business covers all obligations.")
        
        # Rule: Operating cash flow > 0
        if operating_cash_flow > 0:
            green_signals.append(f"Positive operating cash flow (${operating_cash_flow:,.2f}). Operations generate cash.")
        
        # Rule: Advanced mode AND equity injection >= 0.20
        if is_advanced and equity_ratio >= 0.20:
            green_signals.append(f"Equity injection at or above 20% (current: {equity_ratio*100:.1f}%). Strong equity cushion.")
        
        # ========================================
        # DISPLAY
        # ========================================
        
        # Red Flags Section
        st.markdown("### 🔴 Red Flags")
        if red_flags:
            for flag in red_flags:
                st.error(f"🔴 {flag}")
        else:
            st.success("✅ No red flags detected.")
        
        st.divider()
        
        # Yellow Flags Section
        st.markdown("### 🟡 Yellow Flags")
        if yellow_flags:
            for flag in yellow_flags:
                st.warning(f"🟡 {flag}")
        else:
            st.info("✅ No yellow flags detected.")
        
        st.divider()
        
        # Green Signals Section
        st.markdown("### 🟢 Green Signals")
        if green_signals:
            for signal in green_signals:
                st.success(f"🟢 {signal}")
        else:
            st.info("ℹ️ No green signals detected.")
        
        st.divider()
        
        # Debug Output (WPP-INSIGHTS-FLAGS-002)
        with st.expander("🔍 Debug Data (WPP-INSIGHTS-FLAGS-002)"):
            st.markdown("**Rent Ratio Calculation:**")
            st.write(f"- Annual Revenue: ${annual_revenue:,.2f}")
            st.write(f"- Monthly Rent: ${monthly_rent:,.2f}")
            st.write(f"- Annual Rent: ${annual_rent:,.2f}")
            st.write(f"- Rent Ratio: {rent_to_revenue_ratio*100:.2f}%")
            
            if is_advanced:
                st.markdown("**Capital Stack Calculation:**")
                st.write(f"- Total Uses: ${total_uses:,.2f}")
                st.write(f"- Total Sources: ${total_sources:,.2f}")
                st.write(f"- Funding Gap: ${funding_gap:,.2f}")
        
        st.divider()
        
        # Rule Reference
        with st.expander("📋 Flag Rules Reference"):
            st.markdown("""
            **Red Flag Thresholds:**
            - DSCR < 1.0
            - Cash after debt and owner < $0
            - Operating cash flow < $0
            - Capital stack funding gap ≠ $0 (Advanced mode only)
            
            **Yellow Flag Thresholds:**
            - 1.0 ≤ DSCR < 1.20
            - Rent / Revenue > 12%
            - Gross margin < 30%
            - AR days > 30 (Advanced mode only)
            
            **Green Signal Thresholds:**
            - DSCR ≥ 1.25
            - Cash after debt and owner ≥ $0
            - Operating cash flow > $0
            - Equity injection ≥ 20% (Advanced mode only)
            
            *All thresholds are deterministic and rule-based. No subjective analysis.*
            """)
        
    except Exception as e:
        st.error(f"Error analyzing model: {str(e)}")
        st.info("Please ensure all required inputs are configured in the other pages.")
