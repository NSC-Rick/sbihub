import streamlit as st
from sbi_hub.modules.financial_modeler.utils.change_tracker import mark_changes


def render():
    """Render the financing configuration page."""
    st.title("Financing & Working Capital")
    
    st.markdown("""
    Configure loan terms and working capital assumptions.
    The loan amortization will be calculated automatically.
    """)
    
    # Mode Toggle
    st.session_state.mode = st.radio(
        "Model Mode",
        ["Basic", "Advanced"],
        index=0 if st.session_state.mode == "Basic" else 1,
        horizontal=True,
        help="Advanced mode unlocks working capital and capital stack controls",
        on_change=mark_changes
    )
    
    if st.session_state.mode == "Advanced":
        st.info("🔧 **Advanced Mode Active:** Capital Stack and Working Capital controls are available below.")
    
    st.divider()
    
    # Business Stage Selector (Advanced Mode Only)
    if st.session_state.mode == "Advanced":
        st.markdown("### 🏢 Business Stage")
        
        business_stage_display = st.selectbox(
            "Business Stage",
            ["Startup", "Acquisition", "Existing Business"],
            index=["startup", "acquisition", "existing"].index(st.session_state.business_stage),
            help="Determines Period 0 working capital behavior. Startup/Acquisition prevents phantom AP creation.",
            on_change=mark_changes
        )
        
        # Map display value to internal value
        stage_mapping = {
            "Startup": "startup",
            "Acquisition": "acquisition",
            "Existing Business": "existing"
        }
        st.session_state.business_stage = stage_mapping[business_stage_display]
        
        # Show explanation based on stage
        if st.session_state.business_stage in ['startup', 'acquisition']:
            st.info("ℹ️ **Startup/Acquisition mode:** Period 0 assumes no opening Accounts Payable unless explicitly entered below. This prevents overstating liquidity.")
        else:
            st.info("ℹ️ **Existing Business mode:** Period 0 working capital changes calculated from starting balances entered below.")
        
        st.divider()
        
        # Model Mode Toggle (determines opening working capital initialization)
        st.markdown("### 📊 Working Capital Initialization")
        
        model_mode_display = st.radio(
            "Business Scenario",
            ["Startup", "Acquisition"],
            index=0 if st.session_state.get('model_mode', 'startup') == 'startup' else 1,
            horizontal=True,
            help="Determines how opening working capital balances (AR, AP, Inventory) are initialized",
            on_change=mark_changes
        )
        
        # Map display value to internal value
        st.session_state.model_mode = model_mode_display.lower()
        
        # Show explanation based on model mode
        if st.session_state.model_mode == 'startup':
            st.info("🚀 **Startup Mode:** Opening AR, AP, and Inventory balances are zero. Working capital builds from Period 0 operations.")
        else:
            st.info("🏢 **Acquisition Mode:** Opening AR, AP, and Inventory balances are calculated from your operating assumptions (AR days, AP days, Inventory days). This prevents artificial spikes in Period 1.")
        
        st.divider()
        
        # Working Capital Source Toggle
        st.markdown("### 💰 Working Capital Financing")
        
        wc_source_display = st.radio(
            "Working Capital Source",
            ["Buyer Injected", "Seller Provided", "Loan Financed"],
            index=["buyer_injected", "seller_provided", "loan_financed"].index(st.session_state.get('working_capital_source', 'buyer_injected')),
            horizontal=True,
            help="Determines how working capital is financed at closing",
            on_change=mark_changes
        )
        
        # Map display value to internal value
        wc_source_mapping = {
            "Buyer Injected": "buyer_injected",
            "Seller Provided": "seller_provided",
            "Loan Financed": "loan_financed"
        }
        st.session_state.working_capital_source = wc_source_mapping[wc_source_display]
        
        # Show explanation based on working capital source
        if st.session_state.working_capital_source == 'buyer_injected':
            st.info("💵 **Buyer Injected:** Buyer provides cash for working capital. Opening AR, AP, and Inventory are zero. Cash is used to fund operations.")
        elif st.session_state.working_capital_source == 'seller_provided':
            st.info("🤝 **Seller Provided:** Seller transfers working capital balances (AR, AP, Inventory) at closing. No additional cash needed for working capital.")
        else:
            st.info("🏦 **Loan Financed:** Working capital funded by separate loan. Opening balances are zero. Loan proceeds provide cash for operations.")
        
        # Advanced Starting Balances (Optional)
        with st.expander("⚙️ Advanced Starting Balances (Optional)", expanded=False):
            st.markdown("""
            **Optional:** Enter explicit starting balances for working capital accounts.
            - Leave at zero for true startup/acquisition scenarios
            - Enter values for existing business conversions or specific scenarios
            """)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.session_state.starting_ar_balance = st.number_input(
                    "Starting AR Balance",
                    min_value=0.0,
                    value=st.session_state.starting_ar_balance,
                    step=1000.0,
                    help="Accounts Receivable balance at Period 0 start",
                    on_change=mark_changes
                )
            
            with col2:
                st.session_state.starting_ap_balance = st.number_input(
                    "Starting AP Balance",
                    min_value=0.0,
                    value=st.session_state.starting_ap_balance,
                    step=1000.0,
                    help="Accounts Payable balance at Period 0 start (creates supplier credit)",
                    on_change=mark_changes
                )
            
            with col3:
                st.session_state.starting_inventory_balance = st.number_input(
                    "Starting Inventory Balance",
                    min_value=0.0,
                    value=st.session_state.starting_inventory_balance,
                    step=1000.0,
                    help="Inventory balance at Period 0 start",
                    on_change=mark_changes
                )
        
        st.divider()
    
    # Capital Stack Advisory Layer (Collapsible) - Advanced Mode Only
    if st.session_state.mode == "Advanced":
        with st.expander("💼 Acquisition Capital Stack (Optional)", expanded=False):
            st.markdown("""
            **Advisory Tool:** Plan your acquisition financing structure.
            This does not automatically affect the operating model until you click **Apply**.
            """)
        
            st.subheader("Uses of Funds")
            
            # Business Acquisition Section
            st.markdown("### 💼 Business Acquisition")
            
            col1, col2 = st.columns(2)
            
            with col1:
                business_purchase_price = st.number_input(
                    "Business Purchase Price",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['business_purchase_price'],
                    step=10000.0,
                    key="cs_business_purchase_price",
                    help="Purchase price of the business operations and assets",
                    on_change=mark_changes
                )
                
                inventory_adjustment = st.number_input(
                    "Inventory Adjustment",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['inventory_adjustment'],
                    step=1000.0,
                    key="cs_inventory",
                    help="Additional inventory to be purchased",
                    on_change=mark_changes
                )
            
            with col2:
                business_closing_costs = st.number_input(
                    "Business Closing Costs",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['business_closing_costs'],
                    step=1000.0,
                    key="cs_business_closing",
                    help="Legal, accounting, and other business closing costs",
                    on_change=mark_changes
                )
            
            # Calculate total business uses
            total_business_uses = business_purchase_price + inventory_adjustment + business_closing_costs
            
            st.info(f"**Total Business Uses:** ${total_business_uses:,.2f}")
            
            st.divider()
            
            # Real Estate Section
            st.markdown("### 🏢 Real Estate (Optional)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                real_estate_purchase = st.number_input(
                    "Real Estate Purchase",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['real_estate_purchase'],
                    step=10000.0,
                    key="cs_real_estate_purchase",
                    help="Purchase price of real estate property",
                    on_change=mark_changes
                )
            
            with col2:
                real_estate_closing_costs = st.number_input(
                    "Real Estate Closing Costs",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['real_estate_closing_costs'],
                    step=1000.0,
                    key="cs_real_estate_closing",
                    help="Legal, title, and other real estate closing costs",
                    on_change=mark_changes
                )
            
            # Calculate total real estate uses
            total_real_estate_uses = real_estate_purchase + real_estate_closing_costs
            
            st.info(f"**Total Real Estate Uses:** ${total_real_estate_uses:,.2f}")
            
            st.divider()
            
            # Other Uses Section
            st.markdown("### 🔧 Other Uses")
            
            col1, col2 = st.columns(2)
            
            with col1:
                working_capital = st.number_input(
                    "Working Capital Buffer",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['working_capital'],
                    step=1000.0,
                    key="cs_working_capital",
                    help="Cash reserve for operations",
                    on_change=mark_changes
                )
            
            with col2:
                capex = st.number_input(
                    "Minor Capex",
                    min_value=0.0,
                    value=st.session_state.capital_stack['uses']['capex'],
                    step=1000.0,
                    key="cs_capex",
                    help="Minor capital expenditures needed at closing",
                    on_change=mark_changes
                )
            
            # Calculate total uses (aggregation)
            total_uses = total_business_uses + total_real_estate_uses + working_capital + capex
            
            st.divider()
            st.metric("**Total Uses of Funds (Combined)**", f"${total_uses:,.2f}")
        
            st.divider()
        
            st.subheader("Sources of Funds")
        
            st.markdown("**Equity**")
            col1, col2, col3 = st.columns(3)
        
            with col1:
                buyer_equity = st.number_input(
                    "Buyer Equity",
                    min_value=0.0,
                    value=st.session_state.capital_stack['sources']['buyer_equity'],
                    step=5000.0,
                    key="cs_buyer_equity",
                    help="Buyer's cash equity contribution",
                    on_change=mark_changes
                )
        
            with col2:
                community_equity = st.number_input(
                    "Community / Investor Equity",
                    min_value=0.0,
                    value=st.session_state.capital_stack['sources']['community_equity'],
                    step=5000.0,
                    key="cs_community_equity",
                    help="Equity from community investors or partners",
                    on_change=mark_changes
                )
        
            with col3:
                donations = st.number_input(
                    "Donations / Grants",
                    min_value=0.0,
                    value=st.session_state.capital_stack['sources']['donations'],
                    step=1000.0,
                    key="cs_donations",
                    help="Grant funding or donations",
                    on_change=mark_changes
                )
        
            st.markdown("**Debt**")
        
            col1, col2 = st.columns(2)
        
            with col1:
                st.markdown("**Bank Loan**")
                bank_amount = st.number_input(
                    "Bank Loan Amount",
                    min_value=0.0,
                    value=st.session_state.capital_stack['sources']['bank_loan']['amount'],
                    step=5000.0,
                    key="cs_bank_amount",
                    help="Bank loan amount",
                    on_change=mark_changes
                )
            
                bank_rate = st.number_input(
                    "Bank Interest Rate",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.capital_stack['sources']['bank_loan']['rate'],
                    step=0.001,
                    format="%.3f",
                    key="cs_bank_rate",
                    help="Annual interest rate (e.g., 0.06 = 6%)",
                    on_change=mark_changes
                )
            
                bank_term = st.number_input(
                    "Bank Term (Years)",
                    min_value=1,
                    max_value=30,
                    value=int(st.session_state.capital_stack['sources']['bank_loan']['term']),
                    step=1,
                    key="cs_bank_term",
                    help="Loan term in years",
                    on_change=mark_changes
                )
        
            with col2:
                st.markdown("**Seller Note**")
                seller_amount = st.number_input(
                    "Seller Note Amount",
                    min_value=0.0,
                    value=st.session_state.capital_stack['sources']['seller_note']['amount'],
                    step=5000.0,
                    key="cs_seller_amount",
                    help="Seller financing amount",
                    on_change=mark_changes
                )
            
                seller_rate = st.number_input(
                    "Seller Note Rate",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.capital_stack['sources']['seller_note']['rate'],
                    step=0.001,
                    format="%.3f",
                    key="cs_seller_rate",
                    help="Annual interest rate (e.g., 0.05 = 5%)",
                    on_change=mark_changes
                )
            
                seller_term = st.number_input(
                    "Seller Note Term (Years)",
                    min_value=1,
                    max_value=30,
                    value=int(st.session_state.capital_stack['sources']['seller_note']['term']),
                    step=1,
                    key="cs_seller_term",
                    help="Loan term in years",
                    on_change=mark_changes
                )
        
            # Update session state
            st.session_state.capital_stack['uses'] = {
                # Legacy fields (preserved for backward compatibility)
                'purchase_price': business_purchase_price,  # Map to new field for compatibility
                'closing_costs': business_closing_costs,
                # New Business Acquisition fields
                'business_purchase_price': business_purchase_price,
                'inventory_adjustment': inventory_adjustment,
                'business_closing_costs': business_closing_costs,
                # New Real Estate fields
                'real_estate_purchase': real_estate_purchase,
                'real_estate_closing_costs': real_estate_closing_costs,
                # Other uses
                'working_capital': working_capital,
                'capex': capex
            }
        
            st.session_state.capital_stack['sources'] = {
                'buyer_equity': buyer_equity,
                'community_equity': community_equity,
                'donations': donations,
                'bank_loan': {
                    'amount': bank_amount,
                    'rate': bank_rate,
                    'term': bank_term
                },
                'seller_note': {
                    'amount': seller_amount,
                    'rate': seller_rate,
                    'term': seller_term
                }
            }
        
            st.session_state.capital_stack['enabled'] = True
        
            # Calculate totals
            total_equity = buyer_equity + community_equity + donations
            total_debt = bank_amount + seller_amount
            total_sources = total_equity + total_debt
            funding_gap = total_sources - total_uses
        
            st.divider()
        
            st.subheader("Capital Stack Summary")
        
            col1, col2, col3 = st.columns(3)
        
            with col1:
                st.metric("Total Uses", f"${total_uses:,.2f}")
                st.metric("Total Equity", f"${total_equity:,.2f}")
        
            with col2:
                st.metric("Total Sources", f"${total_sources:,.2f}")
                st.metric("Total Debt", f"${total_debt:,.2f}")
        
            with col3:
                if funding_gap == 0:
                    st.metric("Funding Gap", f"${funding_gap:,.2f}", delta="Balanced ✓")
                elif funding_gap > 0:
                    st.metric("Funding Gap", f"${funding_gap:,.2f}", delta="Surplus")
                else:
                    st.metric("Funding Gap", f"${funding_gap:,.2f}", delta="Shortfall ⚠️")
        
            # Calculate annual debt service
            st.divider()
            st.subheader("Advisory Debt Service Analysis")
        
            # Bank loan annual payment
            if bank_amount > 0 and bank_rate > 0:
                annual_bank_payment = bank_amount * (bank_rate * (1 + bank_rate)**bank_term) / ((1 + bank_rate)**bank_term - 1)
            else:
                annual_bank_payment = 0.0
        
            # Seller note annual payment
            if seller_amount > 0 and seller_rate > 0:
                annual_seller_payment = seller_amount * (seller_rate * (1 + seller_rate)**seller_term) / ((1 + seller_rate)**seller_term - 1)
            else:
                annual_seller_payment = 0.0
        
            total_annual_debt_service = annual_bank_payment + annual_seller_payment
        
            col1, col2, col3 = st.columns(3)
        
            with col1:
                st.metric("Annual Bank Payment", f"${annual_bank_payment:,.2f}")
        
            with col2:
                st.metric("Annual Seller Payment", f"${annual_seller_payment:,.2f}")
        
            with col3:
                st.metric("Total Annual Debt Service", f"${total_annual_debt_service:,.2f}")
        
            st.divider()
        
            # Apply button
            st.markdown("### Apply Capital Stack to Operating Model")
            st.markdown("""
            Click the button below to populate the operating model's debt inputs with the capital stack debt structure.
            **This will overwrite existing debt settings.**
            """)
        
            if st.button("🔄 Apply Capital Stack Debt to Operating Model", type="primary"):
                # Map capital stack bank loan to Advanced mode business loan keys
                st.session_state.business_loan_amount = bank_amount
                st.session_state.business_interest_rate = bank_rate
                st.session_state.business_amort_years = bank_term
                
                # Map seller note to Advanced mode real estate loan keys if present
                if seller_amount > 0:
                    st.session_state.real_estate_loan_amount = seller_amount
                    st.session_state.real_estate_interest_rate = seller_rate
                    st.session_state.real_estate_amort_years = seller_term
                    st.success(f"✅ Applied Bank Loan (${bank_amount:,.2f} at {bank_rate:.1%}) to Business Loan and Seller Note (${seller_amount:,.2f} at {seller_rate:.1%}) to Real Estate Loan")
                else:
                    # Clear real estate loan if no seller note
                    st.session_state.real_estate_loan_amount = 0.0
                    st.session_state.real_estate_interest_rate = 0.0
                    st.session_state.real_estate_amort_years = 10
                    st.success(f"✅ Applied Bank Loan: ${bank_amount:,.2f} at {bank_rate:.1%} for {bank_term} years to Business Loan")
                
                # Also update legacy keys for compatibility
                st.session_state.loan_principal = bank_amount + seller_amount
                st.session_state.loan_annual_rate = bank_rate if bank_amount > 0 else 0.0
                st.session_state.loan_term_months = bank_term * 12
                
                st.rerun()
    
    st.divider()
    
    # Initialize loan variables from session state before mode branching
    # This ensures they are always defined before use
    loan_principal = float(st.session_state.get("loan_principal", 0.0))
    loan_annual_rate = float(st.session_state.get("loan_annual_rate", 0.0))
    loan_term_months = int(st.session_state.get("loan_term_months", 60))
    
    # Mode-aware loan structure
    if st.session_state.mode == "Advanced":
        # Dual Loan Structure (Advanced Mode)
        st.subheader("Debt Structure")
        
        st.markdown("""
        Configure separate loans for business and real estate components.
        Manual entry only - no auto-sizing.
        """)
        
        # Business Loan Section
        st.markdown("### 💼 Business Loan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            business_loan_amount = st.number_input(
                "Business Loan Amount",
                min_value=0.0,
                value=st.session_state.business_loan_amount,
                step=1000.0,
                key="business_loan_amount_input",
                help="Loan amount for business acquisition",
                on_change=mark_changes
            )
            st.session_state.business_loan_amount = business_loan_amount
        
        with col2:
            business_interest_rate = st.number_input(
                "Business Interest Rate",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.business_interest_rate,
                step=0.001,
                format="%.3f",
                key="business_interest_rate_input",
                help="Annual interest rate (e.g., 0.06 = 6%)",
                on_change=mark_changes
            )
            st.session_state.business_interest_rate = business_interest_rate
        
        with col3:
            business_amort_years = st.number_input(
                "Business Amortization (Years)",
                min_value=1,
                max_value=30,
                value=int(st.session_state.business_amort_years),
                step=1,
                key="business_amort_years_input",
                help="Amortization period in years",
                on_change=mark_changes
            )
            st.session_state.business_amort_years = business_amort_years
        
        # Calculate business loan payment
        if business_loan_amount > 0 and business_interest_rate > 0:
            monthly_rate = business_interest_rate / 12
            num_payments = business_amort_years * 12
            business_monthly_payment = business_loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            business_monthly_payment = 0.0
        
        st.info(f"**Business Loan Monthly Payment:** ${business_monthly_payment:,.2f}")
        
        st.divider()
        
        # Real Estate Loan Section
        st.markdown("### 🏢 Real Estate Loan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            real_estate_loan_amount = st.number_input(
                "Real Estate Loan Amount",
                min_value=0.0,
                value=st.session_state.real_estate_loan_amount,
                step=1000.0,
                key="real_estate_loan_amount_input",
                help="Loan amount for real estate purchase",
                on_change=mark_changes
            )
            st.session_state.real_estate_loan_amount = real_estate_loan_amount
        
        with col2:
            real_estate_interest_rate = st.number_input(
                "Real Estate Interest Rate",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.real_estate_interest_rate,
                step=0.001,
                format="%.3f",
                key="real_estate_interest_rate_input",
                help="Annual interest rate (e.g., 0.06 = 6%)",
                on_change=mark_changes
            )
            st.session_state.real_estate_interest_rate = real_estate_interest_rate
        
        with col3:
            real_estate_amort_years = st.number_input(
                "Real Estate Amortization (Years)",
                min_value=1,
                max_value=30,
                value=int(st.session_state.real_estate_amort_years),
                step=1,
                key="real_estate_amort_years_input",
                help="Amortization period in years",
                on_change=mark_changes
            )
            st.session_state.real_estate_amort_years = real_estate_amort_years
        
        # Calculate real estate loan payment
        if real_estate_loan_amount > 0 and real_estate_interest_rate > 0:
            monthly_rate = real_estate_interest_rate / 12
            num_payments = real_estate_amort_years * 12
            real_estate_monthly_payment = real_estate_loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            real_estate_monthly_payment = 0.0
        
        st.info(f"**Real Estate Loan Monthly Payment:** ${real_estate_monthly_payment:,.2f}")
        
        st.divider()
        
        # Total Debt Service
        total_monthly_payment = business_monthly_payment + real_estate_monthly_payment
        total_loan_amount = business_loan_amount + real_estate_loan_amount
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("**Total Loan Amount**", f"${total_loan_amount:,.2f}")
        
        with col2:
            st.metric("**Total Monthly Debt Service**", f"${total_monthly_payment:,.2f}")
        
        # Update legacy loan_principal for compatibility with existing model
        loan_principal = total_loan_amount
        st.session_state.loan_principal = loan_principal
        
        if total_loan_amount > 0:
            # Weighted average interest rate
            if business_loan_amount > 0 and real_estate_loan_amount > 0:
                weighted_rate = (business_loan_amount * business_interest_rate + real_estate_loan_amount * real_estate_interest_rate) / total_loan_amount
            elif business_loan_amount > 0:
                weighted_rate = business_interest_rate
            else:
                weighted_rate = real_estate_interest_rate
            loan_annual_rate = weighted_rate
            st.session_state.loan_annual_rate = loan_annual_rate
            
            # Weighted average term
            if business_loan_amount > 0 and real_estate_loan_amount > 0:
                weighted_term = (business_loan_amount * business_amort_years + real_estate_loan_amount * real_estate_amort_years) / total_loan_amount
            elif business_loan_amount > 0:
                weighted_term = business_amort_years
            else:
                weighted_term = real_estate_amort_years
            loan_term_months = int(weighted_term * 12)
            st.session_state.loan_term_months = loan_term_months
        else:
            # No loans in Advanced mode - keep initialized values
            loan_annual_rate = 0.0
            loan_term_months = 60
            st.session_state.loan_annual_rate = loan_annual_rate
            st.session_state.loan_term_months = loan_term_months
    
    else:
        # Single Loan Structure (Basic Mode)
        st.subheader("Term Loan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_principal = st.number_input(
                "Loan Principal",
                min_value=0.0,
                value=st.session_state.loan_principal,
                step=1000.0,
                key="loan_principal_input",
                help="Total loan amount",
                on_change=mark_changes
            )
            st.session_state.loan_principal = loan_principal
            
            loan_annual_rate = st.number_input(
                "Annual Interest Rate",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.loan_annual_rate,
                step=0.001,
                format="%.3f",
                key="loan_rate_input",
                help="Annual interest rate (e.g., 0.06 = 6%)",
                on_change=mark_changes
            )
            st.session_state.loan_annual_rate = loan_annual_rate
        
        with col2:
            loan_term_months = st.number_input(
                "Loan Term (Months)",
                min_value=1,
                value=int(st.session_state.loan_term_months),
                step=12,
                key="loan_term_input",
                help="Loan term in months",
                on_change=mark_changes
            )
            st.session_state.loan_term_months = loan_term_months
            
            max_start_period = st.session_state.periods - 1
            loan_start_period = st.number_input(
                "Start Period (0-indexed)",
                min_value=0,
                max_value=max_start_period,
                value=int(min(st.session_state.loan_start_period, max_start_period)),
                step=1,
                key="loan_start_input",
                help="Period when loan disbursement occurs (0 = first period)",
                on_change=mark_changes
            )
        st.session_state.loan_start_period = loan_start_period
    
    if loan_principal > 0 and loan_annual_rate > 0:
        if st.session_state.time_mode == 'monthly':
            monthly_rate = loan_annual_rate / 12
            payment = loan_principal * (monthly_rate * (1 + monthly_rate)**loan_term_months) / ((1 + monthly_rate)**loan_term_months - 1)
            st.info(f"**Estimated Monthly Payment:** ${payment:,.2f}")
        else:
            payment_years = int((loan_term_months + 11) / 12)
            payment = loan_principal * (loan_annual_rate * (1 + loan_annual_rate)**payment_years) / ((1 + loan_annual_rate)**payment_years - 1)
            st.info(f"**Estimated Annual Payment:** ${payment:,.2f}")
    
    st.divider()
    
    st.subheader("Owner Compensation")
    
    st.markdown("""
    Configure how owner compensation is treated in the financial model.
    - **Payroll**: Included in EBITDA, affects profitability metrics
    - **Distribution**: Deducted from cash after Net Income, does not affect EBITDA
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        owner_mode = st.radio(
            "Treat Owner Compensation As:",
            options=['distribution', 'payroll'],
            index=0 if st.session_state.owner_compensation.get('mode', 'distribution') == 'distribution' else 1,
            key="owner_comp_mode",
            help="Payroll: affects EBITDA and profitability. Distribution: affects only cash flow.",
            on_change=mark_changes
        )
    
    with col2:
        owner_amount = st.number_input(
            "Annual Owner Compensation",
            min_value=0.0,
            value=st.session_state.owner_compensation.get('amount', 0.0),
            step=5000.0,
            key="owner_comp_amount",
            help="Annual amount for owner compensation",
            on_change=mark_changes
        )
    
    st.session_state.owner_compensation = {
        'mode': owner_mode,
        'amount': owner_amount
    }
    
    if owner_mode == 'payroll':
        st.info("💼 Owner compensation will be included as indirect payroll, affecting EBITDA and profitability metrics.")
    else:
        st.info("💰 Owner compensation will be deducted from cash flow after Net Income, preserving EBITDA for underwriting.")
    
    st.divider()
    
    st.subheader("Tax & Depreciation")
    
    st.markdown("""
    Configure corporate tax rate and annual depreciation for P&L statement.
    Taxes are calculated as a flat percentage of pre-tax income (zero if negative).
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        tax_rate = st.number_input(
            "Corporate Tax Rate",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.tax_rate,
            step=0.01,
            format="%.2f",
            key="tax_rate_input",
            help="Corporate tax rate as decimal (e.g., 0.25 = 25%)",
            on_change=mark_changes
        )
        st.session_state.tax_rate = tax_rate
    
    with col2:
        annual_depreciation = st.number_input(
            "Annual Depreciation",
            min_value=0.0,
            value=st.session_state.annual_depreciation,
            step=1000.0,
            key="annual_depreciation_input",
            help="Annual depreciation amount (will be divided by 12 for monthly mode)",
            on_change=mark_changes
        )
        st.session_state.annual_depreciation = annual_depreciation
    
    st.divider()
    
    st.subheader("Working Capital")
    
    st.markdown("""
    Working capital assumptions affect cash flow timing.
    These are converted to cash flow adjustments based on changes in AR, AP, and Inventory.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ar_days = st.number_input(
            "Accounts Receivable Days",
            min_value=0,
            value=int(st.session_state.ar_days),
            step=1,
            key="ar_days_input",
            help="Average days to collect payment from customers",
            on_change=mark_changes
        )
        st.session_state.ar_days = ar_days
    
    with col2:
        ap_days = st.number_input(
            "Accounts Payable Days",
            min_value=0,
            value=int(st.session_state.ap_days),
            step=1,
            key="ap_days_input",
            help="Average days to pay suppliers",
            on_change=mark_changes
        )
        st.session_state.ap_days = ap_days
    
    with col3:
        inventory_days = st.number_input(
            "Inventory Days",
            min_value=0,
            value=int(st.session_state.inventory_days),
            step=1,
            key="inventory_days_input",
            help="Average days inventory is held",
            on_change=mark_changes
        )
        st.session_state.inventory_days = inventory_days
