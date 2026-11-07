import streamlit as st
import pandas as pd
from sbi_hub.modules.financial_modeler.utils.change_tracker import mark_changes

def render():
    """Render the revenue configuration page."""
    st.title("Revenue Streams")
    
    st.markdown("""
    Configure your revenue streams. Each stream has its own price, volume, and growth rate.
    You can optionally override the global COGS percentage for specific streams.
    """)
    
    st.divider()
    
    st.subheader("Global COGS Settings")
    
    global_cogs_pct = st.number_input(
        "Default COGS Percentage",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.global_cogs_pct,
        step=0.01,
        format="%.2f",
        help="Default cost of goods sold as a percentage of revenue (e.g., 0.30 = 30%)",
        on_change=mark_changes
    )
    st.session_state.global_cogs_pct = global_cogs_pct
    
    # COGS Guidance Panel
    st.info("""
**COGS Guidance**

COGS (Cost of Goods Sold) represents the direct costs required to produce your product or deliver your service.

Typical ranges vary by industry:

• **Retail / Product Resale:** 50% – 70%  
• **Restaurants / Food Service:** 28% – 35%  
• **Manufacturing:** 40% – 60%  
• **Construction / Trades:** 30% – 50%  
• **Professional Services:** 5% – 20%  
• **Software / Digital Products:** 0% – 15%

If you are unsure, a starting estimate of **30%** is often reasonable for early-stage projections.

Adjust this value as you refine your assumptions.
""")
    
    # COGS Efficiency Improvement
    if 'cogs_improvement_pct' not in st.session_state:
        st.session_state.cogs_improvement_pct = 0.0
    
    cogs_improvement = st.number_input(
        "COGS Improvement per Year (%)",
        min_value=0.0,
        max_value=10.0,
        step=0.5,
        value=st.session_state.cogs_improvement_pct,
        format="%.1f",
        help="Annual reduction in COGS % as operational efficiency improves (e.g., 2.0 = 2% improvement per year)",
        on_change=mark_changes
    )
    st.session_state.cogs_improvement_pct = cogs_improvement
    
    st.divider()
    
    # Seasonality Controls
    st.subheader("Revenue Seasonality")
    
    st.markdown("""
    Apply seasonal patterns to revenue distribution across months.
    Seasonality affects revenue timing, AR calculations, and inventory proportionally.
    """)
    
    # Retail preset weights (typical retail seasonality)
    RETAIL_PRESET = [6.5, 6.0, 7.5, 8.0, 8.5, 9.0, 9.5, 9.0, 8.0, 9.5, 11.0, 17.5]  # Sums to 100
    
    seasonality_mode = st.radio(
        "Seasonality Mode",
        ["OFF", "Retail Preset", "Custom"],
        index=["OFF", "Retail Preset", "Custom"].index(st.session_state.seasonality['mode']),
        horizontal=True,
        help="OFF: Even distribution. Retail: Holiday-weighted. Custom: Define your own monthly weights",
        on_change=mark_changes
    )
    
    st.session_state.seasonality['mode'] = seasonality_mode
    st.session_state.seasonality['enabled'] = (seasonality_mode != "OFF")
    
    if seasonality_mode == "Retail Preset":
        st.info("📊 **Retail Preset Active:** Revenue weighted toward Q4 holidays (Nov: 11%, Dec: 17.5%)")
        
        # Show visualization
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        chart_data = pd.DataFrame({
            'Month': pd.Categorical(months, categories=months, ordered=True),
            'Weight (%)': RETAIL_PRESET
        })
        st.bar_chart(chart_data.set_index('Month'))
        
    elif seasonality_mode == "Custom":
        st.info("🔧 **Custom Seasonality:** Define monthly revenue weights (will auto-normalize to 100%)")
        
        st.markdown("**Monthly Revenue Weights (%)**")
        
        # Create 3 rows of 4 months each
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        custom_weights = []
        
        for row in range(3):
            cols = st.columns(4)
            for col_idx in range(4):
                month_idx = row * 4 + col_idx
                with cols[col_idx]:
                    weight = st.number_input(
                        months[month_idx],
                        min_value=0.0,
                        max_value=100.0,
                        value=st.session_state.seasonality['custom_weights'][month_idx],
                        step=0.5,
                        key=f"season_weight_{month_idx}",
                        help=f"Revenue weight for {months[month_idx]}"
                    )
                    custom_weights.append(weight)
        
        # Auto-normalize
        total_weight = sum(custom_weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight * 100 for w in custom_weights]
            st.session_state.seasonality['custom_weights'] = normalized_weights
            
            st.caption(f"**Total:** {total_weight:.1f}% → Normalized to 100%")
            
            # Show visualization
            chart_data = pd.DataFrame({
                'Month': pd.Categorical(months, categories=months, ordered=True),
                'Weight (%)': normalized_weights
            })
            st.bar_chart(chart_data.set_index('Month'))
        else:
            st.warning("⚠️ Total weight is 0. Please enter at least one non-zero value.")
    
    st.divider()
    
    # Layered Revenue Input Methods
    st.subheader("Revenue Input Method")
    
    st.markdown("""
    Choose how you want to input revenue data. The system will back-calculate between methods when you switch.
    """)
    
    # Determine available options based on mode
    if st.session_state.mode == "Advanced":
        input_options = ["Monthly Revenue Target", "Average Sale × Monthly Transactions", "Customers per Day × Days Open"]
    else:
        input_options = ["Monthly Revenue Target", "Average Sale × Monthly Transactions"]
    
    # Get previous method to detect changes
    previous_method = st.session_state.revenue_input_method
    
    # Show selector
    revenue_input_method = st.radio(
        "Select Input Method",
        input_options,
        index=input_options.index(previous_method) if previous_method in input_options else 0,
        horizontal=True,
        help="Monthly: Direct revenue input. Avg×Volume: Calculate from transaction data. Customers/Day: Behavioral model (Advanced only)",
        on_change=mark_changes
    )
    
    # Back-calculation logic (ONLY on method change)
    if revenue_input_method != previous_method:
        # Switching FROM Monthly Revenue → Avg × Volume
        if previous_method == "Monthly Revenue Target" and revenue_input_method == "Average Sale × Monthly Transactions":
            if st.session_state.avg_sale > 0:
                st.session_state.monthly_transactions = st.session_state.monthly_revenue / st.session_state.avg_sale
        
        # Switching FROM Avg × Volume → Monthly Revenue
        elif previous_method == "Average Sale × Monthly Transactions" and revenue_input_method == "Monthly Revenue Target":
            st.session_state.monthly_revenue = st.session_state.avg_sale * st.session_state.monthly_transactions
        
        # Switching TO Customers per Day mode
        elif revenue_input_method == "Customers per Day × Days Open":
            if st.session_state.days_open > 0:
                st.session_state.customers_per_day = st.session_state.monthly_transactions / st.session_state.days_open
        
        # Switching FROM Customers per Day mode
        elif previous_method == "Customers per Day × Days Open":
            st.session_state.monthly_transactions = st.session_state.customers_per_day * st.session_state.days_open
            # Also update monthly revenue
            st.session_state.monthly_revenue = st.session_state.avg_sale * st.session_state.monthly_transactions
        
        # Update the stored method
        st.session_state.revenue_input_method = revenue_input_method
    
    # Display inputs based on selected method
    if revenue_input_method == "Monthly Revenue Target":
        st.markdown("**Direct Monthly Revenue Input**")
        
        monthly_revenue = st.number_input(
            "Monthly Revenue Target",
            min_value=0.0,
            value=st.session_state.monthly_revenue,
            step=100.0,
            format="%.2f",
            key="monthly_revenue_input",
            help="Target monthly revenue for this stream",
            on_change=mark_changes
        )
        st.session_state.monthly_revenue = monthly_revenue
        
        st.info(f"💰 **Monthly Revenue:** ${monthly_revenue:,.2f}")
    
    elif revenue_input_method == "Average Sale × Monthly Transactions":
        st.markdown("**Transaction-Based Revenue Calculation**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            avg_sale = st.number_input(
                "Average Sale Amount",
                min_value=0.0,
                value=st.session_state.avg_sale,
                step=1.0,
                format="%.2f",
                key="avg_sale_input",
                help="Average dollar amount per transaction",
                on_change=mark_changes
            )
            st.session_state.avg_sale = avg_sale
        
        with col2:
            monthly_transactions = st.number_input(
                "Monthly Transactions",
                min_value=0.0,
                value=st.session_state.monthly_transactions,
                step=1.0,
                format="%.2f",
                key="monthly_transactions_input",
                help="Number of transactions per month",
                on_change=mark_changes
            )
            st.session_state.monthly_transactions = monthly_transactions
        
        # Calculate and store monthly revenue
        calculated_revenue = avg_sale * monthly_transactions
        st.session_state.monthly_revenue = calculated_revenue
        
        st.info(f"💰 **Calculated Monthly Revenue:** ${calculated_revenue:,.2f} ({monthly_transactions:,.0f} transactions × ${avg_sale:,.2f})")
    
    elif revenue_input_method == "Customers per Day × Days Open":
        st.markdown("**Behavioral Revenue Model (Advanced)**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customers_per_day = st.number_input(
                "Customers per Day",
                min_value=0.0,
                value=st.session_state.customers_per_day,
                step=1.0,
                format="%.2f",
                key="customers_per_day_input",
                help="Average number of customers per day",
                on_change=mark_changes
            )
            st.session_state.customers_per_day = customers_per_day
            
            days_open = st.number_input(
                "Days Open per Month",
                min_value=0.0,
                max_value=31.0,
                value=st.session_state.days_open,
                step=1.0,
                format="%.2f",
                key="days_open_input",
                help="Number of days open per month",
                on_change=mark_changes
            )
            st.session_state.days_open = days_open
        
        with col2:
            avg_sale = st.number_input(
                "Average Sale Amount",
                min_value=0.0,
                value=st.session_state.avg_sale,
                step=1.0,
                format="%.2f",
                key="avg_sale_behavioral_input",
                help="Average dollar amount per customer",
                on_change=mark_changes
            )
            st.session_state.avg_sale = avg_sale
        
        # Calculate monthly transactions and revenue
        calculated_transactions = customers_per_day * days_open
        calculated_revenue = avg_sale * calculated_transactions
        
        st.session_state.monthly_transactions = calculated_transactions
        st.session_state.monthly_revenue = calculated_revenue
        
        st.info(f"📊 **Calculated Monthly Transactions:** {calculated_transactions:,.0f} ({customers_per_day:,.0f} customers/day × {days_open:,.0f} days)")
        st.info(f"💰 **Calculated Monthly Revenue:** ${calculated_revenue:,.2f} ({calculated_transactions:,.0f} transactions × ${avg_sale:,.2f})")
    
    st.divider()
    
    # Startup Revenue Ramp
    st.subheader("Startup Revenue Ramp")
    
    if 'startup_ramp_months' not in st.session_state:
        st.session_state.startup_ramp_months = 0
    
    startup_ramp = st.number_input(
        "Startup Ramp (Months)",
        min_value=0,
        max_value=24,
        step=1,
        value=st.session_state.startup_ramp_months,
        help="Number of months required to reach steady-state revenue. Set to 0 to disable ramp.",
        on_change=mark_changes
    )
    st.session_state.startup_ramp_months = startup_ramp
    
    if startup_ramp > 0:
        st.info(f"""
**Ramp Behavior:** Revenue will gradually increase from 0% to 100% over {startup_ramp} months.

**Typical startup ramps:**
• **Retail:** 3–6 months  
• **Restaurant:** 6–12 months  
• **Service Business:** 3–6 months  
• **Manufacturing:** 12–24 months
""")
    
    st.divider()
    
    st.subheader("Revenue Streams")
    
    for idx, stream in enumerate(st.session_state.revenue_streams):
        with st.expander(f"**{stream['name']}**", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Stream Name",
                    value=stream['name'],
                    key=f"rev_name_{idx}"
                )
                
                price = st.number_input(
                    "Price per Unit",
                    min_value=0.0,
                    value=stream['price'],
                    step=1.0,
                    key=f"rev_price_{idx}",
                    help="Price per unit of product/service"
                )
                
                volume = st.number_input(
                    "Initial Volume",
                    min_value=0.0,
                    value=stream['volume'],
                    step=1.0,
                    key=f"rev_volume_{idx}",
                    help=f"Initial {'monthly' if st.session_state.time_mode == 'monthly' else 'annual'} volume"
                )
            
            with col2:
                growth_rate = st.number_input(
                    f"{'Annual' if st.session_state.time_mode == 'monthly' else 'Annual'} Growth Rate",
                    min_value=-1.0,
                    max_value=10.0,
                    value=stream['growth_rate'],
                    step=0.01,
                    format="%.2f",
                    key=f"rev_growth_{idx}",
                    help="Annual growth rate (e.g., 0.10 = 10% per year)"
                )
                
                use_override = st.checkbox(
                    "Override COGS %",
                    value=stream['cogs_override'] is not None,
                    key=f"rev_cogs_override_check_{idx}"
                )
                
                if use_override:
                    cogs_override = st.number_input(
                        "COGS Percentage",
                        min_value=0.0,
                        max_value=1.0,
                        value=stream['cogs_override'] if stream['cogs_override'] is not None else global_cogs_pct,
                        step=0.01,
                        format="%.2f",
                        key=f"rev_cogs_override_{idx}"
                    )
                else:
                    cogs_override = None
            
            st.session_state.revenue_streams[idx] = {
                'name': name,
                'price': price,
                'volume': volume,
                'growth_rate': growth_rate,
                'cogs_override': cogs_override
            }
            
            if st.button(f"Remove {name}", key=f"remove_rev_{idx}"):
                st.session_state.revenue_streams.pop(idx)
                mark_changes()
                st.rerun()
    
    st.divider()
    
    if st.button("➕ Add Revenue Stream"):
        st.session_state.revenue_streams.append({
            'name': f'Stream {len(st.session_state.revenue_streams) + 1}',
            'price': 100.0,
            'volume': 100.0,
            'growth_rate': 0.10,
            'cogs_override': None
        })
        mark_changes()
        st.rerun()
