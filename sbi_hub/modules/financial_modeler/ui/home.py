import streamlit as st
import json
from datetime import datetime
from sbi_hub.modules.financial_modeler.engine.validation import (
    get_default_model_inputs,
    validate_scenario_json,
    session_state_to_model_inputs,
    model_inputs_to_session_state
)
from sbi_hub.modules.financial_modeler.config.version import PLATFORM_VERSION, BUILD_DATE
from sbi_hub.modules.financial_modeler.utils.session_manager import autosave_session, has_unsaved_changes, get_last_saved_timestamp, mark_unsaved_changes, save_session, load_session
from sbi_hub.modules.financial_modeler.utils.change_tracker import mark_changes

# Check if openpyxl is available for Excel export
try:
    import openpyxl
    from sbi_hub.modules.financial_modeler.utils.excel_export import generate_excel_workbook, get_excel_filename
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    generate_excel_workbook = None
    get_excel_filename = None


def initialize_session_state():
    """Initialize session state with default values."""
    if 'time_mode' not in st.session_state:
        st.session_state.time_mode = 'monthly'
    
    if 'periods' not in st.session_state:
        st.session_state.periods = 36  # Default: 3 years × 12 months
    
    if 'revenue_streams' not in st.session_state:
        st.session_state.revenue_streams = [
            {
                'name': 'Product Sales',
                'price': 100.0,
                'volume': 100.0,
                'growth_rate': 0.10,
                'cogs_override': None
            }
        ]
    
    if 'global_cogs_pct' not in st.session_state:
        st.session_state.global_cogs_pct = 0.30
    
    if 'payroll_roles' not in st.session_state:
        st.session_state.payroll_roles = [
            {
                'role': 'Manager',
                'headcount': 1,
                'pay_type': 'salary',
                'rate': 60000.0,
                'hours_per_week': 40,
                'annual_raise_pct': 0.03,
                'payroll_tax_pct': 0.0765,
                'benefits_pct': 0.15,
                'role_type': 'indirect'
            }
        ]
    else:
        for role in st.session_state.payroll_roles:
            if 'role_type' not in role:
                role['role_type'] = 'indirect'
    
    if 'opex_items' not in st.session_state:
        DEFAULT_OVERHEAD_CATEGORIES = [
            "Rent",
            "Utilities",
            "Heat",
            "Insurance",
            "Maintenance",
            "Subscriptions",
            "Professional Fees",
            "Marketing",
            "Office / Supplies",
            "Miscellaneous"
        ]
        
        st.session_state.opex_items = [
            {
                'name': category,
                'amount': 0.0,
                'growth_rate': 0.03,
                'category': 'fixed'
            }
            for category in DEFAULT_OVERHEAD_CATEGORIES
        ]
    else:
        for item in st.session_state.opex_items:
            if 'category' not in item:
                item['category'] = 'fixed'
    
    # Legacy single loan (preserved for backward compatibility and Basic mode)
    if 'loan_principal' not in st.session_state:
        st.session_state.loan_principal = 0.0
    
    if 'loan_annual_rate' not in st.session_state:
        st.session_state.loan_annual_rate = 0.06
    
    if 'loan_term_months' not in st.session_state:
        st.session_state.loan_term_months = 60
    
    if 'loan_start_period' not in st.session_state:
        st.session_state.loan_start_period = 0
    
    # Dual loan structure (Advanced mode only)
    if 'business_loan_amount' not in st.session_state:
        st.session_state.business_loan_amount = 0.0
    
    if 'business_interest_rate' not in st.session_state:
        st.session_state.business_interest_rate = 0.06
    
    if 'business_amort_years' not in st.session_state:
        st.session_state.business_amort_years = 5
    
    if 'real_estate_loan_amount' not in st.session_state:
        st.session_state.real_estate_loan_amount = 0.0
    
    if 'real_estate_interest_rate' not in st.session_state:
        st.session_state.real_estate_interest_rate = 0.06
    
    if 'real_estate_amort_years' not in st.session_state:
        st.session_state.real_estate_amort_years = 10
    
    # Backward compatibility migration: map legacy loan_principal to business_loan_amount
    if st.session_state.loan_principal > 0 and st.session_state.business_loan_amount == 0.0:
        st.session_state.business_loan_amount = st.session_state.loan_principal
        st.session_state.business_interest_rate = st.session_state.loan_annual_rate
        st.session_state.business_amort_years = st.session_state.loan_term_months / 12
    
    if 'mode' not in st.session_state:
        st.session_state.mode = 'Basic'
    
    if 'ar_days' not in st.session_state:
        st.session_state.ar_days = 0
    
    if 'ap_days' not in st.session_state:
        st.session_state.ap_days = 0
    
    if 'inventory_days' not in st.session_state:
        st.session_state.inventory_days = 0
    
    if 'tax_rate' not in st.session_state:
        st.session_state.tax_rate = 0.25
    
    if 'annual_depreciation' not in st.session_state:
        st.session_state.annual_depreciation = 0.0
    
    if 'owner_compensation' not in st.session_state:
        st.session_state.owner_compensation = {
            'mode': 'distribution',
            'amount': 0.0
        }
    
    if 'business_stage' not in st.session_state:
        st.session_state.business_stage = 'acquisition'
    
    if 'model_mode' not in st.session_state:
        st.session_state.model_mode = 'startup'
    
    if 'working_capital_source' not in st.session_state:
        st.session_state.working_capital_source = 'buyer_injected'
    
    if 'starting_ar_balance' not in st.session_state:
        st.session_state.starting_ar_balance = 0.0
    
    if 'starting_ap_balance' not in st.session_state:
        st.session_state.starting_ap_balance = 0.0
    
    if 'starting_inventory_balance' not in st.session_state:
        st.session_state.starting_inventory_balance = 0.0
    
    if 'capital_stack' not in st.session_state:
        st.session_state.capital_stack = {
            'enabled': False,
            'uses': {
                # Legacy field (preserved for backward compatibility)
                'purchase_price': 0.0,
                'closing_costs': 0.0,
                # New Business Acquisition fields
                'business_purchase_price': 0.0,
                'inventory_adjustment': 0.0,
                'business_closing_costs': 0.0,
                # New Real Estate fields
                'real_estate_purchase': 0.0,
                'real_estate_closing_costs': 0.0,
                # Other uses
                'working_capital': 0.0,
                'capex': 0.0
            },
            'sources': {
                'buyer_equity': 0.0,
                'community_equity': 0.0,
                'donations': 0.0,
                'bank_loan': {
                    'amount': 0.0,
                    'rate': 0.06,
                    'term': 10
                },
                'seller_note': {
                    'amount': 0.0,
                    'rate': 0.05,
                    'term': 5
                }
            }
        }
    
    # Backward compatibility migration: convert legacy purchase_price to new structure
    if 'capital_stack' in st.session_state:
        uses = st.session_state.capital_stack.get('uses', {})
        
        # If legacy purchase_price exists and new fields don't exist, migrate
        if 'purchase_price' in uses and uses.get('purchase_price', 0.0) > 0:
            if 'business_purchase_price' not in uses or uses.get('business_purchase_price', 0.0) == 0.0:
                # Migrate legacy purchase_price to business_purchase_price
                st.session_state.capital_stack['uses']['business_purchase_price'] = uses['purchase_price']
                st.session_state.capital_stack['uses']['real_estate_purchase'] = 0.0
        
        # Ensure all new fields exist with defaults
        if 'business_purchase_price' not in uses:
            st.session_state.capital_stack['uses']['business_purchase_price'] = 0.0
        if 'business_closing_costs' not in uses:
            st.session_state.capital_stack['uses']['business_closing_costs'] = 0.0
        if 'real_estate_purchase' not in uses:
            st.session_state.capital_stack['uses']['real_estate_purchase'] = 0.0
        if 'real_estate_closing_costs' not in uses:
            st.session_state.capital_stack['uses']['real_estate_closing_costs'] = 0.0
    
    if 'seasonality' not in st.session_state:
        st.session_state.seasonality = {
            'enabled': False,
            'mode': 'OFF',  # OFF, Retail, Custom
            'custom_weights': [8.33] * 12  # Default to even distribution (100/12)
        }
    
    # Revenue input method variables
    if 'revenue_input_method' not in st.session_state:
        st.session_state.revenue_input_method = 'Monthly Revenue Target'
    
    if 'monthly_revenue' not in st.session_state:
        st.session_state.monthly_revenue = 0.0
    
    if 'avg_sale' not in st.session_state:
        st.session_state.avg_sale = 25.0
    
    if 'monthly_transactions' not in st.session_state:
        st.session_state.monthly_transactions = 0.0
    
    if 'customers_per_day' not in st.session_state:
        st.session_state.customers_per_day = 0.0
    
    if 'days_open' not in st.session_state:
        st.session_state.days_open = 30.0
    
    # Projection start date (for calendar labeling)
    if 'projection_start_month' not in st.session_state:
        st.session_state.projection_start_month = 1  # January
    
    if 'projection_start_year' not in st.session_state:
        st.session_state.projection_start_year = datetime.now().year
    
    # Modeler variables (persist during session, NOT saved to JSON)
    if 'modeler_revenue_adj' not in st.session_state:
        st.session_state.modeler_revenue_adj = 0.0
    
    if 'modeler_expense_adj' not in st.session_state:
        st.session_state.modeler_expense_adj = 0.0
    
    if 'modeler_scope' not in st.session_state:
        st.session_state.modeler_scope = "Year 1 Only"


def render():
    """Render the home page."""
    initialize_session_state()
    
    st.title("Operating Model")
    st.caption("Structured financial and capital modeling framework")
    
    with st.expander("🎬 Watch the 2-minute Modeler introduction", expanded=False):
        # Custom embed with high-resolution thumbnail (maxresdefault.jpg)
        video_id = "AsUX3rttTZs"
        
        # Create responsive video container with high-res thumbnail
        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
            <iframe 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1&hd=1"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                loading="lazy">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### Welcome to Operating Model
    
    This application helps you build SBDC-style financial models with:
    - **Monthly or Annual** time periods
    - **Multiple revenue streams** with growth projections
    - **Role-based payroll** with raises and benefits
    - **Operating expenses** with inflation
    - **Loan amortization** and debt service coverage
    - **Working capital** management (AR/AP/Inventory)
    
    ### Getting Started
    
    1. **Configure Time Mode** below (Monthly = 36 periods ; Annual = 3 years)
    2. Navigate through the sidebar to input your data
    3. Review your financial statements and KPIs
    
    All calculations are transparent and based on your inputs. No values are fabricated.
    """)
    
    st.divider()
    
    # ========== MEET ERIC SECTION ==========
    st.markdown("### 💬 Meet Eric – Your Financial Modeling Guide")
    
    st.info("""
**Building a financial model is about more than entering numbers—it's about making informed business decisions.**

Eric is your built-in Financial Modeling Guide and is available throughout the application to answer questions about both financial concepts and how to use the Financial Modeler.

**Whether you're wondering:**
- What should I include in Cost of Goods Sold (COGS)?
- How much working capital should I plan for?
- Why did my cash flow change?
- Where should I enter a particular expense?
- How do I interpret a financial ratio or KPI?

**Eric can explain financial concepts, help you navigate the application, and provide guidance on how different assumptions influence your financial projections.**

Think of Eric as having an experienced business advisor sitting beside you while you build your model—ready to answer questions, explain the numbers, and help you gain confidence in your decisions.

**There are no "bad" questions.** If something doesn't make sense, simply ask Eric. Understanding the "why" behind your numbers is just as important as building the model itself.
    """)
    
    st.divider()
    
    # Show unsaved changes banner if needed
    if has_unsaved_changes():
        st.warning("⚠️ **You have unsaved changes.** Save your model to preserve your work.")
    
    st.subheader("Model Management")
    
    st.markdown("""
    Manage your financial model: save, load, export, and restore sessions.
    """)
    
    # ========== SECTION A: SESSION STATUS ==========
    st.markdown("### 📊 Session Status")
    
    col_status1, col_status2 = st.columns([2, 1])
    
    with col_status1:
        # Session recovery status
        saved_session = load_session()
        if saved_session:
            st.info("ℹ️ **Session Recovery Enabled** - Restore your last session anytime")
        else:
            st.info("ℹ️ **Session Protection** - Save your work to enable recovery")
        
        # Last saved timestamp
        last_saved = get_last_saved_timestamp()
        if last_saved:
            time_ago = datetime.now() - last_saved
            if time_ago.seconds < 60:
                time_str = "Just now"
            elif time_ago.seconds < 3600:
                minutes = time_ago.seconds // 60
                time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                hours = time_ago.seconds // 3600
                time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
            st.markdown(f"📅 **Last Saved:** {time_str}")
        else:
            st.markdown("📅 **Last Saved:** Never")
    
    with col_status2:
        # Restore last session button
        if saved_session:
            if st.button("🔄 Restore Last Session", use_container_width=True):
                from sbi_hub.modules.financial_modeler.utils.session_manager import restore_session_data
                if restore_session_data(saved_session):
                    st.session_state['_scroll_to_top'] = True
                    st.success("✅ Session restored!")
                    st.rerun()
        else:
            st.button("🔄 Restore Last Session", disabled=True, use_container_width=True, help="No saved session available")
    
    st.divider()
    
    # ========== SECTION B: SAVE & EXPORT ==========
    st.markdown("### 💾 Save & Export")
    
    # Model name field
    scenario_name = st.text_input(
        "Model Name",
        value=st.session_state.get('scenario_name', "Business Scenario"),
        help="Name your financial model",
        key="scenario_name_input"
    )
    
    # Update session state and mark unsaved if changed
    if scenario_name != st.session_state.get('scenario_name'):
        st.session_state.scenario_name = scenario_name
        mark_unsaved_changes()
    
    # Prepare model data for both save and export
    model_inputs = session_state_to_model_inputs(st.session_state)
    model_inputs['scenario_name'] = scenario_name
    model_inputs['platform_version'] = PLATFORM_VERSION
    model_inputs['build_date'] = BUILD_DATE
    
    # Sanitize filename
    safe_name = scenario_name.strip().replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    col_save, col_export = st.columns(2)
    
    with col_save:
        st.markdown("**Save Model (JSON)**")
        st.caption("💡 Save to reload later in the app")
        
        json_data = json.dumps(model_inputs, indent=2)
        json_filename = f"{safe_name}_{timestamp}.json"
        
        # Download button - automatically saves session after click
        if st.download_button(
            label="💾 Save Model",
            data=json_data,
            file_name=json_filename,
            mime="application/json",
            help="Download model as JSON file",
            use_container_width=True,
            key="save_model_button"
        ):
            # This block executes when button is clicked (before download)
            save_session()
            st.session_state['_just_saved'] = True
    
    with col_export:
        st.markdown("**Export to Excel**")
        st.caption("📊 Spreadsheet for analysis & sharing")
        
        if EXCEL_AVAILABLE:
            excel_data = generate_excel_workbook(model_inputs, scenario_name)
            excel_filename = get_excel_filename(scenario_name)
            
            # Download button - automatically saves session after click
            if st.download_button(
                label="📊 Export to Excel",
                data=excel_data,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download as Excel workbook",
                use_container_width=True,
                key="export_excel_button"
            ):
                # This block executes when button is clicked (before download)
                save_session()
                st.session_state['_just_saved'] = True
        else:
            st.button(
                "📊 Export to Excel",
                disabled=True,
                use_container_width=True,
                help="Excel export unavailable (openpyxl not installed)"
            )
            st.caption("⚠️ Install openpyxl to enable")
    
    st.divider()
    
    # ========== SECTION C: LOAD MODEL ==========
    st.markdown("### 📂 Load Model")
    st.caption("Upload a previously saved JSON model file")
    
    uploaded_file = st.file_uploader(
        "Upload Model",
        type=["json"],
        help="Upload a previously saved model JSON file",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            json_content = uploaded_file.read().decode('utf-8')
            loaded_data = json.loads(json_content)
            
            is_valid, error_msg = validate_scenario_json(loaded_data)
            
            if is_valid:
                model_inputs_to_session_state(loaded_data, st.session_state)
                save_session()  # Automatically clears unsaved flag
                st.session_state['_scroll_to_top'] = True
                st.success("✅ Model loaded successfully!")
                st.rerun()
            else:
                st.error(f"❌ Invalid model file: {error_msg}")
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON file: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
    
    st.divider()
    
    # ========== SECTION D: RESET MODEL ==========
    st.markdown("### 🔄 Reset Model")
    st.caption("Reset all inputs to default values")
    
    # Use session state for confirmation
    if 'show_reset_confirmation' not in st.session_state:
        st.session_state.show_reset_confirmation = False
    
    if not st.session_state.show_reset_confirmation:
        if st.button("🔄 Reset to Defaults", help="Reset all inputs to default values"):
            st.session_state.show_reset_confirmation = True
            st.rerun()
    else:
        st.warning("⚠️ **Are you sure?** This will reset all model inputs to default values. This action cannot be undone.")
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.button("✅ Yes, Reset", type="primary", use_container_width=True):
                defaults = get_default_model_inputs()
                model_inputs_to_session_state(defaults, st.session_state)
                st.session_state.show_reset_confirmation = False
                save_session()  # Automatically clears unsaved flag
                st.session_state['_scroll_to_top'] = True
                st.success("✅ Model reset to defaults!")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_reset_confirmation = False
                st.rerun()
    
    st.divider()
    
    st.subheader("Time Mode Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        time_mode = st.radio(
            "Time Mode",
            options=['monthly', 'annual'],
            index=0 if st.session_state.time_mode == 'monthly' else 1,
            help="Monthly = 36 periods (3 years), Annual = 3 periods (3 years)",
            on_change=mark_changes
        )
        
        if time_mode != st.session_state.time_mode:
            st.session_state.time_mode = time_mode
            st.session_state.periods = 36 if time_mode == 'monthly' else 3
            st.rerun()
    
    with col2:
        st.metric(
            label="Forecast Length",
            value=f"3 Years ({st.session_state.periods} periods)",
            help=f"{'3 years × 12 months' if st.session_state.time_mode == 'monthly' else '3 years'}"
        )
    
    # Projection Start Date
    st.markdown("#### Projection Start Date")
    st.caption("Set the beginning of your projection timeline for calendar-based labeling")
    
    col_month, col_year = st.columns(2)
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    with col_month:
        start_month = st.selectbox(
            "Start Month",
            options=list(range(1, 13)),
            format_func=lambda x: month_names[x-1],
            index=st.session_state.projection_start_month - 1,
            help="First month of your projection",
            key="proj_start_month_select"
        )
        
        if start_month != st.session_state.projection_start_month:
            st.session_state.projection_start_month = start_month
            mark_changes()
    
    with col_year:
        current_year = datetime.now().year
        start_year = st.selectbox(
            "Start Year",
            options=list(range(current_year - 2, current_year + 6)),
            index=st.session_state.projection_start_year - (current_year - 2),
            help="First year of your projection",
            key="proj_start_year_select"
        )
        
        if start_year != st.session_state.projection_start_year:
            st.session_state.projection_start_year = start_year
            mark_changes()
    
    st.divider()
    
    st.info("👈 Use the sidebar to navigate through the model sections.")
