"""
Print-friendly report view for Operating Model.

Generates a clean, formatted report suitable for printing or PDF export.
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render_report(outputs, model_inputs):
    """
    Render a print-friendly report view.
    
    Args:
        outputs: Model outputs from build_model()
        model_inputs: Model inputs dictionary
    """
    
    # Report Header
    st.markdown("# Operating Model Financial Report")
    st.markdown(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    st.markdown(f"**Model Mode:** {model_inputs.get('mode', 'Basic')}")
    st.markdown(f"**Time Period:** {model_inputs['time_mode'].title()} ({model_inputs['periods']} periods)")
    
    # Seasonality info
    seasonality = model_inputs.get('seasonality', {})
    if seasonality.get('enabled'):
        st.markdown(f"**Seasonality:** {seasonality.get('mode', 'OFF')}")
    
    st.divider()
    
    # Income Statement
    st.markdown("## Income Statement")
    st.markdown("*Operating performance by period*")
    
    income_statement = outputs['income_statement'].copy()
    
    # Transpose for report view
    income_transposed = income_statement.T
    income_transposed.columns = [f'Period {i}' for i in income_transposed.columns]
    income_transposed.index.name = 'Line Item'
    
    # Clean up index names
    index_mapping = {
        'revenue': 'Revenue',
        'cogs': 'Cost of Goods Sold',
        'gross_profit': 'Gross Profit',
        'payroll': 'Payroll',
        'opex': 'Operating Expenses',
        'operating_expenses': 'Total Operating Expenses',
        'ebitda': 'EBITDA',
        'interest_expense': 'Interest Expense',
        'net_income': 'Net Income'
    }
    income_transposed.index = [index_mapping.get(idx, idx) for idx in income_transposed.index]
    
    st.dataframe(
        income_transposed.style.format("${:,.2f}"),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Debt Service & Owner Compensation Overlay
    st.markdown("## Cash Flow Analysis")
    st.markdown("*Debt service and owner compensation impact*")
    
    loan_schedule = outputs['loan_schedule']
    owner_comp_config = model_inputs.get('owner_compensation', {'mode': 'distribution', 'amount': 0.0})
    owner_comp_mode = owner_comp_config.get('mode', 'distribution')
    owner_comp_annual = owner_comp_config.get('amount', 0.0)
    
    # Convert owner comp to per-period
    if model_inputs['time_mode'] == 'monthly':
        owner_comp_per_period = owner_comp_annual / 12
    else:
        owner_comp_per_period = owner_comp_annual
    
    # Build overlay
    net_income_row = income_statement['net_income']
    total_debt_service = loan_schedule['payment']
    cash_after_debt = net_income_row - total_debt_service
    
    if owner_comp_mode == 'distribution':
        cash_after_debt_and_owner = cash_after_debt - owner_comp_per_period
    else:
        cash_after_debt_and_owner = cash_after_debt
    
    overlay_df = pd.DataFrame({
        'Net Income': net_income_row,
        'Debt Service (Principal + Interest)': total_debt_service,
        'Cash After Debt': cash_after_debt,
        'Owner Compensation': owner_comp_per_period if owner_comp_mode == 'distribution' else 0,
        'Cash After Debt & Owner': cash_after_debt_and_owner
    })
    
    overlay_transposed = overlay_df.T
    overlay_transposed.columns = [f'Period {i}' for i in overlay_transposed.columns]
    overlay_transposed.index.name = 'Line Item'
    
    st.dataframe(
        overlay_transposed.style.format("${:,.2f}"),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Cash Flow Statement
    st.markdown("## Cash Flow Statement")
    st.markdown("*Cash generation and usage by period*")
    
    cash_flow = outputs['cash_flow_statement'].copy()
    
    # Transpose
    cash_flow_transposed = cash_flow.T
    cash_flow_transposed.columns = [f'Period {i}' for i in cash_flow_transposed.columns]
    cash_flow_transposed.index.name = 'Line Item'
    
    # Clean up index names
    cf_index_mapping = {
        'net_income': 'Net Income',
        'depreciation': 'Depreciation',
        'change_in_ar': 'Change in AR',
        'change_in_ap': 'Change in AP',
        'change_in_inventory': 'Change in Inventory',
        'operating_cash_flow': 'Operating Cash Flow',
        'principal_payment': 'Principal Payment',
        'owner_distribution': 'Owner Distribution',
        'net_cash_flow': 'Net Cash Flow',
        'cumulative_cash': 'Cumulative Cash'
    }
    cash_flow_transposed.index = [cf_index_mapping.get(idx, idx) for idx in cash_flow_transposed.index]
    
    st.dataframe(
        cash_flow_transposed.style.format("${:,.2f}"),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Capital Stack (if Advanced mode)
    if model_inputs.get('mode') == 'Advanced':
        capital_stack = model_inputs.get('capital_stack', {})
        if capital_stack.get('enabled'):
            st.markdown("## Capital Stack Summary")
            st.markdown("*Acquisition financing structure*")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Uses of Funds")
                uses = capital_stack.get('uses', {})
                uses_data = {
                    'Purchase Price': uses.get('purchase_price', 0),
                    'Inventory Adjustment': uses.get('inventory_adjustment', 0),
                    'Closing Costs': uses.get('closing_costs', 0),
                    'Working Capital': uses.get('working_capital', 0),
                    'Minor Capex': uses.get('capex', 0)
                }
                total_uses = sum(uses_data.values())
                uses_data['**Total Uses**'] = total_uses
                
                uses_df = pd.DataFrame(list(uses_data.items()), columns=['Item', 'Amount'])
                st.dataframe(
                    uses_df.style.format({'Amount': '${:,.2f}'}),
                    hide_index=True,
                    use_container_width=True
                )
            
            with col2:
                st.markdown("### Sources of Funds")
                sources = capital_stack.get('sources', {})
                sources_data = {
                    'Buyer Equity': sources.get('buyer_equity', 0),
                    'Community Equity': sources.get('community_equity', 0),
                    'Donations/Grants': sources.get('donations', 0),
                    'Bank Loan': sources.get('bank_loan', {}).get('amount', 0),
                    'Seller Note': sources.get('seller_note', {}).get('amount', 0)
                }
                total_sources = sum(sources_data.values())
                sources_data['**Total Sources**'] = total_sources
                
                sources_df = pd.DataFrame(list(sources_data.items()), columns=['Item', 'Amount'])
                st.dataframe(
                    sources_df.style.format({'Amount': '${:,.2f}'}),
                    hide_index=True,
                    use_container_width=True
                )
            
            funding_gap = total_sources - total_uses
            if funding_gap == 0:
                st.success(f"✅ **Funding Gap:** ${funding_gap:,.2f} (Balanced)")
            elif funding_gap > 0:
                st.info(f"ℹ️ **Funding Gap:** ${funding_gap:,.2f} (Surplus)")
            else:
                st.warning(f"⚠️ **Funding Gap:** ${funding_gap:,.2f} (Shortfall)")
            
            st.markdown("---")
    
    # Working Capital Summary (if Advanced mode)
    if model_inputs.get('mode') == 'Advanced':
        ar_days = model_inputs.get('ar_days', 0)
        ap_days = model_inputs.get('ap_days', 0)
        inventory_days = model_inputs.get('inventory_days', 0)
        
        if ar_days > 0 or ap_days > 0 or inventory_days > 0:
            st.markdown("## Working Capital Summary")
            st.markdown("*Cash conversion cycle assumptions*")
            
            wc_data = {
                'Accounts Receivable Days': ar_days,
                'Accounts Payable Days': ap_days,
                'Inventory Days': inventory_days,
                '**Cash Conversion Cycle**': ar_days + inventory_days - ap_days
            }
            
            wc_df = pd.DataFrame(list(wc_data.items()), columns=['Metric', 'Days'])
            st.dataframe(
                wc_df,
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("---")
    
    # Key Metrics
    st.markdown("## Key Performance Metrics")
    st.markdown("*Summary financial ratios and indicators*")
    
    kpis = outputs['kpis']
    
    # Get first period metrics
    first_period_kpis = kpis.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("DSCR", f"{first_period_kpis.get('dscr', 0):.2f}")
        st.metric("Gross Margin %", f"{first_period_kpis.get('gross_margin_pct', 0):.1f}%")
    
    with col2:
        st.metric("Net Margin %", f"{first_period_kpis.get('net_margin_pct', 0):.1f}%")
        st.metric("EBITDA Margin %", f"{first_period_kpis.get('ebitda_margin_pct', 0):.1f}%")
    
    with col3:
        st.metric("Break-Even Revenue", f"${first_period_kpis.get('break_even_revenue', 0):,.2f}")
        st.metric("Contribution Margin %", f"{first_period_kpis.get('contribution_margin_pct', 0):.1f}%")
    
    st.markdown("---")
    
    # Footer
    st.caption("*This report was generated by Operating Model - Structured Financial Modeling Framework*")
    st.caption(f"*Report Date: {datetime.now().strftime('%B %d, %Y')}*")
