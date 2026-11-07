import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sbi_hub.modules.financial_modeler.engine.model import build_model
from sbi_hub.modules.financial_modeler.engine.validation import validate_scenario_json
from sbi_hub.modules.financial_modeler.utils.formatters import safe_currency, safe_ratio, safe_percentage
from sbi_hub.modules.financial_modeler.utils.period_labels import format_dataframe_with_period_labels
from sbi_hub.modules.financial_modeler.ui.report_view import render_report
from sbi_hub.modules.financial_modeler.analysis.financial_metrics import compute_financial_metrics


def render():
    """Render the review page with financial statements and charts."""
    st.title("Review & Analysis")
    
    st.markdown("""
    Review your complete financial model including income statement, cash flow statement, and key metrics.
    """)
    
    # Generate Report button
    if st.button("📄 Generate Print Report", type="primary", help="Create a print-friendly report view"):
        st.session_state.show_report = True
    
    # Show report if requested
    if st.session_state.get('show_report', False):
        st.divider()
        st.markdown("## 📄 Print Report View")
        st.caption("This view is optimized for printing or PDF export. Use your browser's print function (Ctrl+P or Cmd+P).")
        
        if st.button("← Back to Analysis View"):
            st.session_state.show_report = False
            st.rerun()
    
    model_inputs = {
        'time_mode': st.session_state.time_mode,
        'periods': st.session_state.periods,
        'revenue_streams': st.session_state.revenue_streams,
        'global_cogs_pct': st.session_state.global_cogs_pct,
        'payroll_roles': st.session_state.payroll_roles,
        'opex_items': st.session_state.opex_items,
        'loan_principal': st.session_state.loan_principal,
        'loan_annual_rate': st.session_state.loan_annual_rate,
        'loan_term_months': st.session_state.loan_term_months,
        'loan_start_period': st.session_state.loan_start_period,
        'ar_days': st.session_state.ar_days,
        'ap_days': st.session_state.ap_days,
        'inventory_days': st.session_state.inventory_days,
        'tax_rate': st.session_state.tax_rate,
        'annual_depreciation': st.session_state.annual_depreciation,
        'owner_compensation': st.session_state.owner_compensation,
        'mode': st.session_state.mode,
        'capital_stack': st.session_state.capital_stack,
        'seasonality': st.session_state.seasonality,
        'business_stage': st.session_state.business_stage,
        'starting_ar_balance': st.session_state.starting_ar_balance,
        'starting_ap_balance': st.session_state.starting_ap_balance,
        'starting_inventory_balance': st.session_state.starting_inventory_balance,
        'model_mode': st.session_state.get('model_mode', 'startup'),
        'working_capital_source': st.session_state.get('working_capital_source', 'buyer_injected')
    }
    
    try:
        with st.spinner("Building financial model..."):
            outputs = build_model(model_inputs)
        
        # Store summary metrics in session_state for Modeler page
        income_statement = outputs['income_statement']
        cash_flow_statement = outputs.get('cash_flow', None)
        loan_schedule = outputs['loan_schedule']
        kpis = outputs['kpis']
        
        # Log warning if cash_flow is missing
        if cash_flow_statement is None:
            print("MODEL WARNING: cash_flow output missing from financial model")
        
        # Compute canonical financial metrics (single source of truth)
        # Only compute if cash_flow_statement is available
        owner_comp_config = model_inputs.get('owner_compensation', {'mode': 'distribution', 'amount': 0.0})
        if cash_flow_statement is not None:
            canonical_metrics = compute_financial_metrics(
                income_statement,
                cash_flow_statement,
                loan_schedule,
                owner_comp_config,
                model_inputs['time_mode']
            )
        else:
            canonical_metrics = None
        
        # Store DataFrames in session state for Excel export
        # Income statement transposed (rows = line items, columns = periods)
        income_transposed = income_statement.T
        income_transposed.columns = [f'Period {i}' for i in income_transposed.columns]
        income_transposed.index.name = 'Line Item'
        st.session_state.income_statement_df = income_transposed
        
        # Cash flow transposed
        if 'cash_flow' in outputs:
            cash_flow = outputs['cash_flow']
            cash_flow_transposed = cash_flow.T
            cash_flow_transposed.columns = [f'Period {i}' for i in cash_flow_transposed.columns]
            cash_flow_transposed.index.name = 'Line Item'
            st.session_state.cash_flow_df = cash_flow_transposed
        
        # Revenue forecast transposed
        if 'revenue_df' in outputs:
            revenue_df = outputs['revenue_df']
            revenue_transposed = revenue_df.T
            revenue_transposed.columns = [f'Period {i}' for i in revenue_transposed.columns]
            revenue_transposed.index.name = 'Revenue Stream'
            st.session_state.revenue_df = revenue_transposed
        
        # KPIs transposed
        kpis_transposed = kpis.T
        kpis_transposed.columns = [f'Period {i}' for i in kpis_transposed.columns]
        kpis_transposed.index.name = 'Metric'
        st.session_state.kpis_df = kpis_transposed
        
        # Store canonical DSCR series (if available)
        if canonical_metrics is not None:
            st.session_state.dscr_series = canonical_metrics['dscr_series']
        else:
            st.session_state.dscr_series = kpis.get('dscr', pd.Series())
        
        # Calculate Year 1 metrics using canonical source
        if st.session_state.time_mode == 'monthly':
            year1_periods = min(12, len(income_statement))
            year1_revenue = income_statement['revenue'][:year1_periods].sum()
            year1_operating_expenses = income_statement['operating_expenses'][:year1_periods].sum()
            year1_net_income = income_statement['net_income'][:year1_periods].sum()
            year1_debt_service = loan_schedule['payment'][:year1_periods].sum()
            year1_cash_flow = year1_net_income - year1_debt_service
            year1_ebitda = income_statement['ebitda'][:year1_periods].sum()
            # Use canonical DSCR calculation
            year1_dscr = year1_ebitda / year1_debt_service if year1_debt_service > 0 else None
        else:
            year1_revenue = income_statement['revenue'].iloc[0]
            year1_operating_expenses = income_statement['operating_expenses'].iloc[0]
            year1_net_income = income_statement['net_income'].iloc[0]
            year1_debt_service = loan_schedule['payment'].iloc[0]
            year1_cash_flow = year1_net_income - year1_debt_service
            year1_ebitda = income_statement['ebitda'].iloc[0]
            # Use canonical DSCR calculation
            year1_dscr = year1_ebitda / year1_debt_service if year1_debt_service > 0 else None
        
        # Store in session_state for Modeler
        st.session_state.review_summary_metrics = {
            'year1_revenue': year1_revenue,
            'year1_operating_expenses': year1_operating_expenses,
            'year1_net_income': year1_net_income,
            'year1_debt_service': year1_debt_service,
            'year1_cash_flow': year1_cash_flow,
            'year1_dscr': year1_dscr
        }
        
        # If report view requested, render report and return
        if st.session_state.get('show_report', False):
            render_report(outputs, model_inputs)
            return
        
        st.success("✅ Model built successfully!")
        
        st.divider()
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Income Statement",
            "💰 Cash Flow",
            "🏦 Loan Schedule",
            "📈 KPIs",
            "📉 Charts"
        ])
        
        with tab1:
            st.subheader("Income Statement")
            
            # Add toggle for dollar vs % of revenue view
            income_view = st.radio(
                "Display Format:",
                options=['Dollar', '% of Revenue'],
                horizontal=True,
                key='income_view_toggle'
            )
            
            income_statement = outputs['income_statement'].copy()
            
            # Transpose: line items as rows, periods as columns
            income_transposed = income_statement.T
            
            # Apply calendar-based period labels
            start_month = st.session_state.get('projection_start_month', 1)
            start_year = st.session_state.get('projection_start_year', 2026)
            time_mode = st.session_state.get('time_mode', 'monthly')
            
            income_transposed = format_dataframe_with_period_labels(
                income_transposed, start_month, start_year, time_mode
            )
            income_transposed.index.name = 'Line Item'
            
            # Convert to % of revenue if selected
            if income_view == '% of Revenue':
                income_display = income_transposed.copy()
                
                # Get revenue row for each period
                revenue_row = income_statement['revenue']
                
                # Convert each column (period) to % of revenue
                for col_idx, period in enumerate(income_display.columns):
                    revenue_value = revenue_row.iloc[col_idx]
                    
                    if revenue_value != 0:
                        # Divide each line item by revenue for this period
                        income_display[period] = (income_transposed[period] / revenue_value) * 100
                    else:
                        # Avoid divide by zero - set to 0
                        income_display[period] = 0
                
                st.dataframe(
                    income_display.style.format("{:.2f}%"),
                    use_container_width=True
                )
                
                download_data = income_display.to_csv()
                download_filename = "income_statement_percent.csv"
            else:
                # Dollar view
                income_display = income_transposed
                
                st.dataframe(
                    income_display.style.format("${:,.2f}"),
                    use_container_width=True
                )
                
                download_data = income_display.to_csv()
                download_filename = "income_statement.csv"
            
            st.download_button(
                label=f"Download Income Statement ({income_view}) (CSV)",
                data=download_data,
                file_name=download_filename,
                mime="text/csv"
            )
            
            # Overlay section: Debt Service and Owner Compensation
            st.divider()
            st.markdown("### Cash Flow Analysis")
            st.caption("Supplemental analysis showing debt service and owner compensation impact on cash")
            
            # Get loan schedule for debt service calculation
            loan_schedule = outputs['loan_schedule']
            
            # Get owner compensation configuration
            owner_comp_config = st.session_state.owner_compensation
            owner_comp_mode = owner_comp_config.get('mode', 'distribution')
            owner_comp_annual = owner_comp_config.get('amount', 0.0)
            
            # Convert owner comp to per-period
            if st.session_state.time_mode == 'monthly':
                owner_comp_per_period = owner_comp_annual / 12
            else:
                owner_comp_per_period = owner_comp_annual
            
            # Build overlay dataframe
            overlay_data = {}
            
            # Get Net Income from income statement
            net_income_row = income_statement['net_income']
            
            # Total debt service per period (principal + interest)
            total_debt_service = loan_schedule['payment']
            
            # Calculate cash metrics
            cash_after_debt = net_income_row - total_debt_service
            
            # Only subtract owner comp if in distribution mode
            if owner_comp_mode == 'distribution':
                cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
            else:
                # In payroll mode, owner comp already in income statement
                cash_after_debt_and_owner = cash_after_debt
            
            # Build overlay dataframe with same structure as income statement
            overlay_df = pd.DataFrame({
                'Net Income': net_income_row,
                'Debt Service (Principal + Interest)': total_debt_service,
                'Cash After Debt': cash_after_debt,
                'Owner Compensation': owner_comp_per_period if owner_comp_mode == 'distribution' else 0,
                'Cash After Debt & Owner': cash_after_debt_and_owner
            })
            
            # Transpose to match income statement format
            overlay_transposed = overlay_df.T
            
            # Apply calendar-based period labels
            start_month = st.session_state.get('projection_start_month', 1)
            start_year = st.session_state.get('projection_start_year', 2026)
            time_mode = st.session_state.get('time_mode', 'monthly')
            
            overlay_transposed = format_dataframe_with_period_labels(
                overlay_transposed, start_month, start_year, time_mode
            )
            overlay_transposed.index.name = 'Line Item'
            
            # Display based on selected view
            if income_view == '% of Revenue':
                overlay_display = overlay_transposed.copy()
                revenue_row = income_statement['revenue']
                
                for col_idx, period in enumerate(overlay_display.columns):
                    revenue_value = revenue_row.iloc[col_idx]
                    if revenue_value != 0:
                        overlay_display[period] = (overlay_transposed[period] / revenue_value) * 100
                    else:
                        overlay_display[period] = 0
                
                st.dataframe(
                    overlay_display.style.format("{:.2f}%"),
                    use_container_width=True
                )
            else:
                st.dataframe(
                    overlay_transposed.style.format("${:,.2f}"),
                    use_container_width=True
                )
            
            # Add explanatory note
            if owner_comp_mode == 'payroll':
                st.info("ℹ️ Owner compensation is treated as **Payroll** and already included in the Income Statement above. Cash After Debt & Owner equals Cash After Debt.")
            else:
                st.info(f"ℹ️ Owner compensation (${owner_comp_annual:,.2f}/year) is treated as **Distribution** and deducted from cash after debt service.")
        
        with tab2:
            st.subheader("Cash Flow Statement")
            
            # Show note about AP behavior in startup/acquisition mode
            if model_inputs.get('business_stage') in ['startup', 'acquisition'] and model_inputs.get('starting_ap_balance', 0.0) == 0:
                st.info("ℹ️ **Startup/Acquisition mode:** Period 0 assumes no opening Accounts Payable unless explicitly entered. This prevents overstating liquidity from phantom supplier credit.")
            
            # Defensive handling for missing cash_flow_statement
            if 'cash_flow_statement' in outputs and outputs['cash_flow_statement'] is not None:
                cash_flow = outputs['cash_flow_statement'].copy()
                
                # Show model mode banner
                model_mode = model_inputs.get('model_mode', 'startup')
                if model_mode == 'startup':
                    st.info("🚀 **Startup Mode** — No opening working capital balances assumed. AR, AP, and Inventory build from Period 0 operations.")
                else:
                    st.info("🏢 **Acquisition Mode** — Opening AR/AP/Inventory initialized from operating assumptions. This prevents artificial spikes in Period 1.")
                
                # Show capital stack funding indicator
                capital_metrics = cash_flow.attrs.get('capital_metrics', {})
                beginning_cash = capital_metrics.get('beginning_cash', 0)
                if beginning_cash > 0:
                    st.info(f"💰 **Beginning Cash funded from Capital Stack:** ${beginning_cash:,.0f}")
                
                # Transpose: line items as rows, periods as columns
                cash_flow_transposed = cash_flow.T
                
                # Apply calendar-based period labels
                start_month = st.session_state.get('projection_start_month', 1)
                start_year = st.session_state.get('projection_start_year', 2026)
                time_mode = st.session_state.get('time_mode', 'monthly')
                
                cash_flow_transposed = format_dataframe_with_period_labels(
                    cash_flow_transposed, start_month, start_year, time_mode
                )
                cash_flow_transposed.index.name = 'Line Item'
                
                st.dataframe(
                    cash_flow_transposed.style.format("${:,.2f}"),
                    use_container_width=True
                )
                
                st.download_button(
                    label="Download Cash Flow (CSV)",
                    data=cash_flow_transposed.to_csv(),
                    file_name="cash_flow.csv",
                    mime="text/csv"
                )
                
                # Cash Requirement Summary Panel
                st.divider()
                st.subheader("💰 Cash Requirement Summary")
                
                # Get capital metrics from cash flow statement attributes
                capital_metrics = cash_flow.attrs.get('capital_metrics', {})
                
                if capital_metrics:
                    lowest_cash_balance = capital_metrics.get('lowest_cash_balance', 0)
                    cash_injection_required = capital_metrics.get('cash_injection_required', 0)
                    lowest_cash_period = capital_metrics.get('lowest_cash_period', 0)
                    recommended_starting_cash = capital_metrics.get('recommended_starting_cash', 0)
                    break_even_period = capital_metrics.get('break_even_period', None)
                    
                    # Warning indicator if capital is required
                    if cash_injection_required > 0:
                        st.warning(
                            f"⚠️ **Startup capital required:** ${cash_injection_required:,.0f} minimum to avoid negative cash"
                        )
                    else:
                        st.success("✅ **No additional startup capital required** - business generates positive cash from Period 0")
                    
                    # Summary table
                    summary_df = pd.DataFrame({
                        "Metric": [
                            "Lowest Cash Balance",
                            "Occurs In Period",
                            "Minimum Cash Injection Required",
                            "Recommended Starting Cash (10% buffer)",
                            "Break-Even Period"
                        ],
                        "Value": [
                            f"${lowest_cash_balance:,.0f}",
                            lowest_cash_period,
                            f"${cash_injection_required:,.0f}",
                            f"${recommended_starting_cash:,.0f}",
                            break_even_period if break_even_period is not None else "N/A"
                        ]
                    })
                    
                    st.table(summary_df)
                    
                    # Explanatory note
                    st.caption("""
                    **How to use this summary:**
                    - **Lowest Cash Balance:** The most negative cash point in your projection
                    - **Minimum Cash Injection:** The amount needed to keep cash non-negative
                    - **Recommended Starting Cash:** Includes a 10% safety buffer for practical planning
                    - **Break-Even Period:** First period where the business becomes cash positive
                    """)
                    
                    # Required Working Capital Panel
                    st.divider()
                    st.subheader("📊 Required Working Capital Analysis")
                    
                    required_wc = capital_metrics.get('required_working_capital', 0)
                    required_wc_ar = capital_metrics.get('required_wc_ar', 0)
                    required_wc_ap = capital_metrics.get('required_wc_ap', 0)
                    required_wc_inventory = capital_metrics.get('required_wc_inventory', 0)
                    wc_coverage = capital_metrics.get('working_capital_coverage', None)
                    wc_source = capital_metrics.get('working_capital_source', 'buyer_injected')
                    beginning_cash = capital_metrics.get('beginning_cash', 0)
                    
                    # Display working capital source
                    wc_source_display = {
                        'buyer_injected': '💵 Buyer Injected',
                        'seller_provided': '🤝 Seller Provided',
                        'loan_financed': '🏦 Loan Financed'
                    }.get(wc_source, wc_source)
                    
                    st.info(f"**Working Capital Source:** {wc_source_display}")
                    
                    # Required working capital breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Required Working Capital Components:**")
                        wc_components_df = pd.DataFrame({
                            "Component": [
                                "Accounts Receivable",
                                "Inventory",
                                "Accounts Payable",
                                "Net Working Capital"
                            ],
                            "Amount": [
                                f"${required_wc_ar:,.0f}",
                                f"${required_wc_inventory:,.0f}",
                                f"-${required_wc_ap:,.0f}",
                                f"${required_wc:,.0f}"
                            ]
                        })
                        st.table(wc_components_df)
                    
                    with col2:
                        st.markdown("**Working Capital Coverage:**")
                        
                        if wc_coverage is not None and required_wc > 0:
                            # Coverage ratio interpretation
                            if wc_coverage < 1.0:
                                coverage_status = "⚠️ Undercapitalized"
                                coverage_color = "warning"
                            elif wc_coverage < 1.5:
                                coverage_status = "✅ Adequate"
                                coverage_color = "success"
                            else:
                                coverage_status = "💪 Strong Liquidity"
                                coverage_color = "success"
                            
                            st.metric(
                                label="Coverage Ratio",
                                value=f"{wc_coverage:.2f}x",
                                help="Beginning Cash / Required Working Capital"
                            )
                            
                            if coverage_color == "warning":
                                st.warning(f"{coverage_status}")
                            else:
                                st.success(f"{coverage_status}")
                            
                            st.caption(f"""
                            **Beginning Cash:** ${beginning_cash:,.0f}  
                            **Required WC:** ${required_wc:,.0f}  
                            **Coverage:** {wc_coverage:.2f}x
                            
                            **Interpretation:**
                            - < 1.0x: Undercapitalized
                            - 1.0-1.5x: Adequate
                            - > 1.5x: Strong liquidity
                            """)
                        else:
                            st.info("Coverage ratio not applicable (negative or zero required WC)")
                else:
                    st.info("💡 Capital requirement metrics not available.")
            else:
                st.info("💡 Cash flow statement not available in current model configuration.")
        
        with tab3:
            st.subheader("Loan Amortization Schedule")
            
            loan_schedule = outputs['loan_schedule'].copy()
            
            # Apply calendar-based period labels
            start_month = st.session_state.get('projection_start_month', 1)
            start_year = st.session_state.get('projection_start_year', 2026)
            time_mode = st.session_state.get('time_mode', 'monthly')
            
            loan_schedule = format_dataframe_with_period_labels(
                loan_schedule, start_month, start_year, time_mode
            )
            
            st.dataframe(
                loan_schedule.style.format("${:,.2f}"),
                use_container_width=True
            )
            
            st.download_button(
                label="Download Loan Schedule (CSV)",
                data=loan_schedule.to_csv(),
                file_name="loan_schedule.csv",
                mime="text/csv"
            )
        
        with tab4:
            st.subheader("Key Performance Indicators")
            
            kpis = outputs['kpis'].copy()
            
            # Apply calendar-based period labels
            start_month = st.session_state.get('projection_start_month', 1)
            start_year = st.session_state.get('projection_start_year', 2026)
            time_mode = st.session_state.get('time_mode', 'monthly')
            
            kpis = format_dataframe_with_period_labels(
                kpis, start_month, start_year, time_mode
            )
            kpis.index.name = 'Period'
            
            # Use safe formatters to handle None/NaN values
            format_dict = {
                'ebitda': lambda x: safe_currency(x),
                'debt_service': lambda x: safe_currency(x),
                'dscr': lambda x: safe_ratio(x),
                'ending_cash': lambda x: safe_currency(x)
            }
            
            if 'net_income' in kpis.columns:
                format_dict['net_income'] = lambda x: safe_currency(x)
                format_dict['taxes'] = lambda x: safe_currency(x)
                format_dict['net_margin'] = lambda x: safe_percentage(x)
            
            st.dataframe(
                kpis.style.format(format_dict),
                use_container_width=True
            )
            
            st.markdown("### 🎯 Key Underwriting Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Use canonical metrics for DSCR (if available)
                if canonical_metrics is not None:
                    avg_dscr = canonical_metrics['avg_dscr']
                    total_debt_service = canonical_metrics['total_debt_service']
                else:
                    # Fallback to KPIs if canonical metrics not available
                    dscr_values = kpis.get('dscr', pd.Series()).dropna()
                    avg_dscr = dscr_values.mean() if len(dscr_values) > 0 else None
                    total_debt_service = kpis.get('debt_service', pd.Series()).sum()
                
                if total_debt_service == 0 or avg_dscr is None:
                    # Debt-free scenario
                    st.metric(
                        label="⭐ Average DSCR",
                        value="—",
                        help="Debt Service Coverage Ratio = EBITDA / Total Debt Service. No debt obligations."
                    )
                    st.success("🟢 Debt Free")
                    st.caption("No debt obligations")
                else:
                    # Use canonical average DSCR
                    st.metric(
                        label="⭐ Average DSCR",
                        value=f"{avg_dscr:.2f}",
                        help="Debt Service Coverage Ratio = EBITDA / Total Debt Service. Lenders typically require 1.25+"
                    )
                    
                    if avg_dscr >= 1.25:
                        st.success("✅ Strong debt coverage")
                    elif avg_dscr >= 1.0:
                        st.warning("⚠️ Marginal debt coverage")
                    else:
                        st.error("❌ Insufficient debt coverage")
            
            with col2:
                if 'break_even_revenue' in kpis.columns:
                    break_even = kpis['break_even_revenue'].iloc[0]
                    if st.session_state.time_mode == 'monthly':
                        total_revenue = outputs['pnl_statement']['revenue'].sum()
                    else:
                        total_revenue = outputs['pnl_statement']['revenue'].iloc[0] if len(outputs['pnl_statement']) > 0 else 0
                    
                    st.metric(
                        label="💰 Break-Even Revenue (Annual)",
                        value=safe_currency(break_even, decimals=0, placeholder="N/A"),
                        help="Annual revenue needed to cover all fixed costs, owner salary, and debt service"
                    )
                    
                    if not pd.isna(break_even) and total_revenue > 0:
                        if st.session_state.time_mode == 'monthly':
                            coverage = (total_revenue / break_even) if break_even > 0 else 0
                        else:
                            coverage = (total_revenue / break_even) if break_even > 0 else 0
                        
                        if coverage >= 1.5:
                            st.success(f"✅ {coverage:.1f}x coverage")
                        elif coverage >= 1.0:
                            st.warning(f"⚠️ {coverage:.1f}x coverage")
                        else:
                            st.error(f"❌ {coverage:.1f}x coverage")
            
            with col3:
                if 'contribution_margin_pct' in kpis.columns:
                    avg_contrib_margin = kpis['contribution_margin_pct'].mean()
                    st.metric(
                        label="📊 Contribution Margin %",
                        value=f"{avg_contrib_margin:.1%}",
                        help="(Revenue - Variable Costs) / Revenue. Higher is better for covering fixed costs."
                    )
                    if avg_contrib_margin >= 0.40:
                        st.success("✅ Strong margin")
                    elif avg_contrib_margin >= 0.25:
                        st.info("ℹ️ Moderate margin")
                    else:
                        st.warning("⚠️ Thin margin")
            
            st.divider()
            
            # Working Capital Panel
            st.markdown("### 💼 Working Capital Requirement")
            
            # Get working capital data from cash flow statement
            if 'cash_flow_statement' in outputs and outputs['cash_flow_statement'] is not None:
                cash_flow = outputs['cash_flow_statement']
                
                # Get working capital requirement from debug metadata
                period_0_debug = cash_flow.attrs.get('period_0_debug', {})
                wc_requirement = period_0_debug.get('working_capital_requirement', 0)
                
                if 'ar_change' in cash_flow.columns and 'inventory_change' in cash_flow.columns and 'ap_change' in cash_flow.columns:
                    ar_period_0 = cash_flow['ar_change'].iloc[0]
                    inv_period_0 = cash_flow['inventory_change'].iloc[0]
                    ap_period_0 = cash_flow['ap_change'].iloc[0]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            label="💰 Working Capital Requirement",
                            value=safe_currency(wc_requirement, decimals=0),
                            help="Total working capital needed for Period 0 operations (AR + Inventory - AP)"
                        )
                        
                        if wc_requirement > 0:
                            st.info(f"✅ Required for operations")
                        else:
                            st.success("✅ No requirement")
                    
                    with col2:
                        # Calculate Period 0 ending cash
                        period_0_ending_cash = cash_flow['ending_cash'].iloc[0]
                        st.metric(
                            label="💵 Period 0 Ending Cash",
                            value=safe_currency(period_0_ending_cash, decimals=0),
                            help="Cash balance at end of Period 0 (may be negative without startup capital)"
                        )
                        
                        if period_0_ending_cash >= 0:
                            st.success("✅ Positive cash position")
                        else:
                            st.error("❌ Negative cash - see Cash Requirement Summary below")
                    
                    with col3:
                        st.metric(
                            label="📊 WC Components (Period 0)",
                            value=safe_currency(wc_requirement, decimals=0),
                            help=f"AR: {safe_currency(ar_period_0, decimals=0)}\nInventory: {safe_currency(inv_period_0, decimals=0)}\nAP: {safe_currency(ap_period_0, decimals=0)}"
                        )
                        
                        # Show breakdown
                        with st.expander("📋 Working Capital Breakdown"):
                            st.markdown(f"""
                            **Period 0 Working Capital Components:**
                            - **Accounts Receivable:** {safe_currency(ar_period_0, decimals=0)}
                            - **Inventory:** {safe_currency(inv_period_0, decimals=0)}
                            - **Accounts Payable:** {safe_currency(ap_period_0, decimals=0)}
                            - **Net Requirement:** {safe_currency(wc_requirement, decimals=0)}
                            
                            *Working Capital = (AR + Inventory) - AP*
                            
                            Note: This shows the working capital requirement. The actual cash needed
                            is shown in the **Cash Requirement Summary** below the Cash Flow Statement.
                            """)
            
            st.divider()
            
            st.markdown("### 💵 Financial Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                final_cash = kpis['ending_cash'].iloc[-1]
                st.metric(
                    label="Final Ending Cash",
                    value=safe_currency(final_cash)
                )
            
            with col2:
                if 'net_income' in kpis.columns:
                    final_net_income = kpis['net_income'].iloc[-1]
                    st.metric(
                        label="Final Net Income",
                        value=safe_currency(final_net_income)
                    )
            
            with col3:
                if 'gross_margin' in kpis.columns:
                    avg_gross_margin = kpis['gross_margin'].mean()
                    st.metric(
                        label="Avg Gross Margin %",
                        value=safe_percentage(avg_gross_margin, decimals=1)
                    )
            
            with col4:
                if 'taxes' in kpis.columns:
                    total_taxes = kpis['taxes'].sum()
                    st.metric(
                        label="Total Taxes (3Y)",
                        value=safe_currency(total_taxes)
                    )
            
            st.download_button(
                label="Download KPIs (CSV)",
                data=kpis.to_csv(),
                file_name="kpis.csv",
                mime="text/csv"
            )
        
        with tab5:
            st.subheader("Visualizations")
            
            # Generate calendar-based period labels for charts
            from sbi_hub.modules.financial_modeler.utils.period_labels import generate_period_labels
            start_month = st.session_state.get('projection_start_month', 1)
            start_year = st.session_state.get('projection_start_year', 2026)
            time_mode = st.session_state.get('time_mode', 'monthly')
            period_labels = generate_period_labels(start_month, start_year, st.session_state.periods, time_mode)
            
            fig_revenue = go.Figure()
            
            # Add actual revenue line
            fig_revenue.add_trace(go.Scatter(
                x=period_labels,
                y=outputs['income_statement']['revenue'].values,
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # If startup ramp is enabled, show full steady-state revenue
            startup_ramp = st.session_state.get('startup_ramp_months', 0)
            if startup_ramp > 0 and st.session_state.time_mode == 'monthly':
                # Calculate full revenue without ramp
                full_revenue = []
                for period in range(st.session_state.periods):
                    if startup_ramp > 0 and period < startup_ramp:
                        ramp_factor = (period + 1) / startup_ramp
                        full_rev = outputs['income_statement']['revenue'].values[period] / ramp_factor if ramp_factor > 0 else 0
                    else:
                        full_rev = outputs['income_statement']['revenue'].values[period]
                    full_revenue.append(full_rev)
                
                fig_revenue.add_trace(go.Scatter(
                    x=period_labels,
                    y=full_revenue,
                    mode='lines',
                    name='Full Revenue (Steady-State)',
                    line=dict(color='#1f77b4', width=1, dash='dash'),
                    opacity=0.5
                ))
                
                # Add shaded ramp period
                fig_revenue.add_vrect(
                    x0=0,
                    x1=startup_ramp,
                    fillcolor="lightgray",
                    opacity=0.2,
                    line_width=0,
                    annotation_text=f"Ramp Period ({startup_ramp} months)",
                    annotation_position="top left"
                )
            
            fig_revenue.update_layout(
                title="Revenue Trend",
                xaxis_title="Period",
                yaxis_title="Revenue ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
            
            # Ending cash chart (only if cash_flow_statement available)
            if 'cash_flow_statement' in outputs and outputs['cash_flow_statement'] is not None:
                fig_cash = go.Figure()
                fig_cash.add_trace(go.Scatter(
                    x=period_labels,
                    y=outputs['cash_flow_statement']['ending_cash'].values,
                    mode='lines+markers',
                    name='Ending Cash',
                    line=dict(color='#2ca02c', width=2),
                    fill='tozeroy'
                ))
                fig_cash.update_layout(
                    title="Ending Cash Balance",
                    xaxis_title="Period",
                    yaxis_title="Cash ($)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_cash, use_container_width=True)
            
            dscr_data = kpis[kpis['dscr'] > 0]['dscr']
            if len(dscr_data) > 0:
                fig_dscr = go.Figure()
                fig_dscr.add_trace(go.Scatter(
                    x=dscr_data.index.tolist(),
                    y=dscr_data.values,
                    mode='lines+markers',
                    name='DSCR',
                    line=dict(color='#ff7f0e', width=2)
                ))
                fig_dscr.add_hline(
                    y=1.25,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Target DSCR = 1.25"
                )
                fig_dscr.update_layout(
                    title="Debt Service Coverage Ratio (DSCR)",
                    xaxis_title="Period",
                    yaxis_title="DSCR",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_dscr, use_container_width=True)
            else:
                st.info("No debt service payments in this model period.")
    
    except Exception as e:
        st.error(f"Error building model: {str(e)}")
        st.exception(e)
