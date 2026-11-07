import streamlit as st
from sbi_hub.modules.financial_modeler.utils.change_tracker import mark_changes


def render():
    """Render the operating expenses configuration page."""
    st.title("Operating Expenses")
    
    st.markdown("""
    Configure your operating expenses (excluding payroll) with support for:
    - **Fixed**: Set amount with growth rate (e.g., rent, insurance)
    - **Semi-Fixed**: Set amount with growth rate (e.g., utilities, maintenance)
    - **Variable % Revenue**: Percentage of revenue per period (e.g., commissions, credit card fees)
    """)
    
    st.divider()
    
    st.subheader("Operating Expense Items")
    st.caption("Common overhead categories are preloaded. Modify as needed.")
    
    for idx, item in enumerate(st.session_state.opex_items):
        with st.expander(f"**{item['name']}**", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                name = st.text_input(
                    "Expense Name",
                    value=item['name'],
                    key=f"opex_name_{idx}",
                    on_change=mark_changes
                )
                
                category = st.selectbox(
                    "Category",
                    options=['fixed', 'semi-fixed', 'variable_pct_revenue'],
                    index=['fixed', 'semi-fixed', 'variable_pct_revenue'].index(item.get('category', 'fixed')),
                    key=f"opex_category_{idx}",
                    help="Fixed: grows by rate. Semi-Fixed: grows by rate. Variable: % of revenue",
                    on_change=mark_changes
                )
            
            with col2:
                if category == 'variable_pct_revenue':
                    amount = st.number_input(
                        "Percentage of Revenue",
                        min_value=0.0,
                        max_value=1.0,
                        value=item['amount'] if item.get('category') == 'variable_pct_revenue' else 0.05,
                        step=0.01,
                        format="%.2f",
                        key=f"opex_amount_{idx}",
                        help="Percentage of revenue (e.g., 0.03 = 3%)",
                        on_change=mark_changes
                    )
                    growth_rate = 0.0
                else:
                    amount = st.number_input(
                        f"{'Monthly' if st.session_state.time_mode == 'monthly' else 'Annual'} Amount",
                        min_value=0.0,
                        value=item['amount'],
                        step=100.0,
                        key=f"opex_amount_{idx}",
                        help=f"Initial {'monthly' if st.session_state.time_mode == 'monthly' else 'annual'} expense amount",
                        on_change=mark_changes
                    )
            
            with col3:
                if category != 'variable_pct_revenue':
                    growth_rate = st.number_input(
                        "Annual Growth Rate",
                        min_value=-1.0,
                        max_value=10.0,
                        value=item.get('growth_rate', 0.03),
                        step=0.01,
                        format="%.2f",
                        key=f"opex_growth_{idx}",
                        help="Annual growth rate (e.g., 0.03 = 3% inflation)",
                        on_change=mark_changes
                    )
                else:
                    growth_rate = 0.0
                    st.info("Variable expenses scale with revenue automatically")
            
            st.session_state.opex_items[idx] = {
                'name': name,
                'amount': amount,
                'growth_rate': growth_rate,
                'category': category
            }
            
            if st.button(f"Remove {name}", key=f"remove_opex_{idx}"):
                st.session_state.opex_items.pop(idx)
                mark_changes()
                st.rerun()
    
    st.divider()
    
    if st.button("➕ Add Operating Expense"):
        st.session_state.opex_items.append({
            'name': f'Expense {len(st.session_state.opex_items) + 1}',
            'amount': 0.0,
            'growth_rate': 0.03,
            'category': 'fixed'
        })
        mark_changes()
        st.rerun()
