import streamlit as st
from sbi_hub.modules.financial_modeler.utils.change_tracker import mark_changes


def render():
    """Render the payroll configuration page."""
    st.title("Payroll & Personnel")
    
    st.markdown("""
    Configure your payroll roles with headcount, compensation, and benefits.
    Supports both hourly and salaried employees with automatic raise calculations.
    """)
    
    st.divider()
    
    st.subheader("Payroll Roles")
    
    for idx, role in enumerate(st.session_state.payroll_roles):
        with st.expander(f"**{role['role']}**", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                role_name = st.text_input(
                    "Role Title",
                    value=role['role'],
                    key=f"payroll_role_{idx}",
                    on_change=mark_changes
                )
                
                headcount = st.number_input(
                    "Headcount",
                    min_value=0,
                    value=role['headcount'],
                    step=1,
                    key=f"payroll_headcount_{idx}",
                    help="Number of employees in this role",
                    on_change=mark_changes
                )
                
                pay_type = st.selectbox(
                    "Pay Type",
                    options=['salary', 'hourly'],
                    index=0 if role['pay_type'] == 'salary' else 1,
                    key=f"payroll_paytype_{idx}",
                    on_change=mark_changes
                )
                
                role_type = st.selectbox(
                    "Role Type",
                    options=['indirect', 'direct'],
                    index=0 if role.get('role_type', 'indirect') == 'indirect' else 1,
                    key=f"payroll_roletype_{idx}",
                    help="Direct: flows to COGS (production labor). Indirect: flows to Operating Expenses (overhead)",
                    on_change=mark_changes
                )
            
            with col2:
                if pay_type == 'salary':
                    rate = st.number_input(
                        "Annual Salary",
                        min_value=0.0,
                        value=role['rate'],
                        step=1000.0,
                        key=f"payroll_rate_{idx}",
                        help="Annual salary per employee",
                        on_change=mark_changes
                    )
                    hours_per_week = 40
                else:
                    rate = st.number_input(
                        "Hourly Rate",
                        min_value=0.0,
                        value=role['rate'],
                        step=0.5,
                        key=f"payroll_rate_{idx}",
                        help="Hourly wage",
                        on_change=mark_changes
                    )
                    hours_per_week = st.number_input(
                        "Hours per Week",
                        min_value=0.0,
                        max_value=168.0,
                        value=float(role.get('hours_per_week', 40)),
                        step=1.0,
                        key=f"payroll_hours_{idx}",
                        on_change=mark_changes
                    )
                
                annual_raise_pct = st.number_input(
                    "Annual Raise %",
                    min_value=0.0,
                    max_value=1.0,
                    value=role['annual_raise_pct'],
                    step=0.01,
                    format="%.2f",
                    key=f"payroll_raise_{idx}",
                    help="Annual raise percentage (e.g., 0.03 = 3%)",
                    on_change=mark_changes
                )
            
            with col3:
                payroll_tax_pct = st.number_input(
                    "Payroll Tax %",
                    min_value=0.0,
                    max_value=1.0,
                    value=role['payroll_tax_pct'],
                    step=0.01,
                    format="%.4f",
                    key=f"payroll_tax_{idx}",
                    help="Employer payroll taxes (e.g., 0.0765 = 7.65% for FICA)",
                    on_change=mark_changes
                )
                
                benefits_pct = st.number_input(
                    "Benefits %",
                    min_value=0.0,
                    max_value=1.0,
                    value=role['benefits_pct'],
                    step=0.01,
                    format="%.2f",
                    key=f"payroll_benefits_{idx}",
                    help="Benefits as % of wages (e.g., 0.15 = 15%)",
                    on_change=mark_changes
                )
            
            st.session_state.payroll_roles[idx] = {
                'role': role_name,
                'headcount': headcount,
                'pay_type': pay_type,
                'rate': rate,
                'hours_per_week': hours_per_week,
                'annual_raise_pct': annual_raise_pct,
                'payroll_tax_pct': payroll_tax_pct,
                'benefits_pct': benefits_pct,
                'role_type': role_type
            }
            
            if st.button(f"Remove {role_name}", key=f"remove_payroll_{idx}"):
                st.session_state.payroll_roles.pop(idx)
                mark_changes()
                st.rerun()
    
    st.divider()
    
    if st.button("➕ Add Payroll Role"):
        st.session_state.payroll_roles.append({
            'role': f'Role {len(st.session_state.payroll_roles) + 1}',
            'headcount': 1,
            'pay_type': 'salary',
            'rate': 50000.0,
            'hours_per_week': 40,
            'annual_raise_pct': 0.03,
            'payroll_tax_pct': 0.0765,
            'benefits_pct': 0.15,
            'role_type': 'indirect'
        })
        mark_changes()
        st.rerun()
