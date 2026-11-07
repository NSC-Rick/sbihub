import pandas as pd
import numpy as np


def safe_divide(numerator: float, denominator: float) -> float:
    """
    Safely divide two numbers, returning 0.0 if denominator is zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
    
    Returns:
        Result of division, or 0.0 if denominator is zero
    """
    if denominator in (0, 0.0, None) or pd.isna(denominator):
        return 0.0
    return numerator / denominator


def calculate_margin(value: float, revenue: float) -> float:
    """
    Calculate margin percentage.
    
    Args:
        value: Numerator (profit, EBITDA, etc.)
        revenue: Revenue (denominator)
    
    Returns:
        Margin as decimal (e.g., 0.22 for 22%)
    """
    return safe_divide(value, revenue)


def calculate_working_capital_requirement(inventory, ar, ap):
    """
    Calculate total working capital required to operate the business.
    
    Working capital = Current Assets - Current Liabilities
    = (Inventory + Accounts Receivable) - Accounts Payable
    
    Args:
        inventory: Inventory balance
        ar: Accounts receivable balance
        ap: Accounts payable balance
    
    Returns:
        Total working capital requirement
    """
    return inventory + ar - ap


def calculate_opening_working_capital(
    model_mode,
    revenue_period_0,
    cogs_period_0,
    ar_days,
    ap_days,
    inventory_days,
    days_in_period=30
):
    """
    Calculate opening working capital balances based on model mode.
    
    Args:
        model_mode: 'startup' or 'acquisition'
        revenue_period_0: Revenue for period 0
        cogs_period_0: COGS for period 0
        ar_days: Days sales outstanding
        ap_days: Days payable outstanding
        inventory_days: Days inventory held
        days_in_period: Days in period (default 30 for monthly)
    
    Returns:
        Dictionary with opening AR, AP, and Inventory balances
    """
    if model_mode == 'startup':
        # Startup mode: Zero opening balances
        return {
            'ar': 0.0,
            'ap': 0.0,
            'inventory': 0.0
        }
    elif model_mode == 'acquisition':
        # Acquisition mode: Calculate from operating assumptions
        opening_ar = revenue_period_0 * (ar_days / days_in_period)
        opening_ap = cogs_period_0 * (ap_days / days_in_period)
        opening_inventory = cogs_period_0 * (inventory_days / days_in_period)
        
        return {
            'ar': opening_ar,
            'ap': opening_ap,
            'inventory': opening_inventory
        }
    else:
        # Default to startup mode for unknown values
        return {
            'ar': 0.0,
            'ap': 0.0,
            'inventory': 0.0
        }


def calculate_required_working_capital(
    revenue,
    cogs,
    ar_days,
    ap_days,
    inventory_days,
    days_in_period=30
):
    """
    Calculate required working capital based on operating assumptions.
    
    Args:
        revenue: Revenue for the period
        cogs: COGS for the period
        ar_days: Days sales outstanding
        ap_days: Days payable outstanding
        inventory_days: Days inventory held
        days_in_period: Days in period (default 30 for monthly)
    
    Returns:
        Dictionary with AR, AP, Inventory balances and required working capital
    """
    ar_balance = revenue * (ar_days / days_in_period)
    ap_balance = cogs * (ap_days / days_in_period)
    inventory_balance = cogs * (inventory_days / days_in_period)
    
    # Required working capital = Current Assets - Current Liabilities
    # = (AR + Inventory) - AP
    required_wc = ar_balance + inventory_balance - ap_balance
    
    return {
        'ar': ar_balance,
        'ap': ap_balance,
        'inventory': inventory_balance,
        'required_wc': required_wc
    }


def build_income_statement(revenue_total, cogs, payroll_total, opex_total, interest_expense):
    """
    Build income statement.
    
    Args:
        revenue_total: Series of total revenue per period
        cogs: Series of COGS per period
        payroll_total: Series of total payroll per period
        opex_total: Series of total opex per period
        interest_expense: Series of interest expense per period
    
    Returns:
        DataFrame with income statement line items
    """
    gross_profit = revenue_total - cogs
    operating_expenses = payroll_total + opex_total
    ebitda = gross_profit - operating_expenses
    ebit = ebitda
    ebt = ebit - interest_expense
    net_income = ebt
    
    return pd.DataFrame({
        'revenue': revenue_total,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'payroll': payroll_total,
        'opex': opex_total,
        'operating_expenses': operating_expenses,
        'ebitda': ebitda,
        'interest_expense': interest_expense,
        'net_income': net_income
    })


def build_cash_flow_statement(net_income, loan_principal, loan_payment, ar_days, ap_days, inventory_days, 
                               revenue_total, cogs, time_mode, owner_distribution=None, 
                               business_stage='acquisition', starting_ar_balance=0.0, 
                               starting_ap_balance=0.0, starting_inventory_balance=0.0,
                               capital_stack_enabled=False, beginning_cash=0.0, model_mode='startup',
                               working_capital_source='buyer_injected'):
    """
    Build cash flow statement with working capital adjustments and owner distributions.
    
    Model mode determines opening working capital initialization:
    - 'startup': Zero opening balances (default)
    - 'acquisition': Opening balances calculated from operating assumptions
    
    Working capital source determines how working capital is financed:
    - 'buyer_injected': Buyer provides cash for working capital (default)
    - 'seller_provided': Seller provides working capital balances (AR, AP, Inventory)
    - 'loan_financed': Working capital funded by separate loan
    
    Prevents Period-0 AP double counting in startup/acquisition scenarios.
    Beginning cash can be funded from capital stack working capital.
    
    Args:
        net_income: Series of net income per period
        loan_principal: Series of loan principal payments per period
        loan_payment: Series of total loan payments per period
        ar_days: Days sales outstanding (AR)
        ap_days: Days payable outstanding (AP)
        inventory_days: Days inventory held
        revenue_total: Series of revenue per period
        cogs: Series of COGS per period
        time_mode: 'monthly' or 'annual'
        owner_distribution: Optional Series of owner distribution per period
        business_stage: 'startup', 'acquisition', or 'existing'
        starting_ar_balance: Explicit starting AR balance (default 0.0)
        starting_ap_balance: Explicit starting AP balance (default 0.0)
        starting_inventory_balance: Explicit starting inventory balance (default 0.0)
        capital_stack_enabled: Whether capital stack funding is enabled
        beginning_cash: Beginning cash balance (from capital stack)
        model_mode: 'startup' or 'acquisition' (default 'startup')
    
    Returns:
        DataFrame with cash flow statement including working_capital_injection row
    """
    periods = len(net_income)
    
    days_in_period = 30 if time_mode == 'monthly' else 365
    
    # Determine if this is a startup-like scenario
    is_startup_like = business_stage in ['startup', 'acquisition'] or capital_stack_enabled
    
    # Calculate opening working capital balances based on working_capital_source and model_mode
    # Priority: explicit starting balances > working_capital_source > model_mode
    if starting_ar_balance != 0.0 or starting_ap_balance != 0.0 or starting_inventory_balance != 0.0:
        # Explicit starting balances provided (legacy behavior - highest priority)
        opening_wc = {
            'ar': starting_ar_balance,
            'ap': starting_ap_balance,
            'inventory': starting_inventory_balance
        }
    elif working_capital_source == 'seller_provided':
        # Seller provides working capital balances (AR, AP, Inventory)
        # Calculate required working capital from operating assumptions
        required_wc = calculate_required_working_capital(
            revenue=revenue_total.iloc[0] if len(revenue_total) > 0 else 0.0,
            cogs=cogs.iloc[0] if len(cogs) > 0 else 0.0,
            ar_days=ar_days,
            ap_days=ap_days,
            inventory_days=inventory_days,
            days_in_period=days_in_period
        )
        opening_wc = {
            'ar': required_wc['ar'],
            'ap': required_wc['ap'],
            'inventory': required_wc['inventory']
        }
    elif working_capital_source in ['buyer_injected', 'loan_financed']:
        # Buyer injects cash or loan finances working capital
        # Opening balances are zero (cash is provided instead)
        opening_wc = {
            'ar': 0.0,
            'ap': 0.0,
            'inventory': 0.0
        }
    else:
        # Fallback to model_mode logic
        opening_wc = calculate_opening_working_capital(
            model_mode=model_mode,
            revenue_period_0=revenue_total.iloc[0] if len(revenue_total) > 0 else 0.0,
            cogs_period_0=cogs.iloc[0] if len(cogs) > 0 else 0.0,
            ar_days=ar_days,
            ap_days=ap_days,
            inventory_days=inventory_days,
            days_in_period=days_in_period
        )
    
    # Calculate target working capital balances for each period
    target_ar_balance = revenue_total * (ar_days / days_in_period)
    target_ap_balance = cogs * (ap_days / days_in_period)
    target_inventory_balance = cogs * (inventory_days / days_in_period)
    
    # Initialize change series
    ar_change = pd.Series([0.0] * periods, index=range(periods))
    ap_change = pd.Series([0.0] * periods, index=range(periods))
    inventory_change = pd.Series([0.0] * periods, index=range(periods))
    
    # Track ending balances for each period
    ar_ending_balance = pd.Series([0.0] * periods, index=range(periods))
    ap_ending_balance = pd.Series([0.0] * periods, index=range(periods))
    inventory_ending_balance = pd.Series([0.0] * periods, index=range(periods))
    
    # Calculate changes period by period
    for period in range(periods):
        if period == 0:
            # Period 0: Use opening balances from model_mode
            beginning_ar = opening_wc['ar']
            beginning_ap = opening_wc['ap']
            beginning_inventory = opening_wc['inventory']
            
            # CRITICAL: In startup mode, force AP to zero in Period 0 to prevent phantom supplier credit
            if model_mode == 'startup' and beginning_ap == 0.0:
                # Startup mode: No AP in Period 0
                ap_change.iloc[0] = 0.0
                ap_ending_balance.iloc[0] = 0.0
            else:
                # Acquisition mode or explicit starting balances: Calculate normally
                ap_change.iloc[0] = target_ap_balance.iloc[0] - beginning_ap
                ap_ending_balance.iloc[0] = target_ap_balance.iloc[0]
            
            # AR and Inventory build normally from opening balances
            ar_change.iloc[0] = target_ar_balance.iloc[0] - beginning_ar
            inventory_change.iloc[0] = target_inventory_balance.iloc[0] - beginning_inventory
            
            # Set ending balances
            ar_ending_balance.iloc[0] = target_ar_balance.iloc[0]
            inventory_ending_balance.iloc[0] = target_inventory_balance.iloc[0]
        else:
            # Period 1+: Use prior period ending balances
            beginning_ar = ar_ending_balance.iloc[period - 1]
            beginning_ap = ap_ending_balance.iloc[period - 1]
            beginning_inventory = inventory_ending_balance.iloc[period - 1]
            
            ar_change.iloc[period] = target_ar_balance.iloc[period] - beginning_ar
            ap_change.iloc[period] = target_ap_balance.iloc[period] - beginning_ap
            inventory_change.iloc[period] = target_inventory_balance.iloc[period] - beginning_inventory
            
            ar_ending_balance.iloc[period] = target_ar_balance.iloc[period]
            ap_ending_balance.iloc[period] = target_ap_balance.iloc[period]
            inventory_ending_balance.iloc[period] = target_inventory_balance.iloc[period]
    
    # Calculate working capital requirement for Period 0 (for diagnostics only)
    # Note: This uses ending balances, not changes
    if len(target_ar_balance) > 0:
        period_0_inventory = inventory_ending_balance.iloc[0]
        period_0_ar = ar_ending_balance.iloc[0]
        period_0_ap = ap_ending_balance.iloc[0]
        working_capital_requirement = calculate_working_capital_requirement(
            period_0_inventory, 
            period_0_ar, 
            period_0_ap
        )
    else:
        working_capital_requirement = 0
    
    # Calculate operating cash flow
    operating_cash_flow = net_income - ar_change + ap_change - inventory_change
    
    # Financing cash flow includes loan principal payments
    financing_cash_flow = -loan_principal
    
    # Owner distribution
    if owner_distribution is not None:
        owner_dist = owner_distribution
    else:
        owner_dist = pd.Series([0.0] * periods, index=range(periods))
    
    # Net cash flow (financially pure - no artificial injections)
    net_cash_flow = operating_cash_flow + financing_cash_flow - owner_dist
    
    # Ending cash balance: beginning cash + cumulative net cash flow
    # beginning_cash comes from capital stack working capital (if enabled)
    ending_cash = beginning_cash + net_cash_flow.cumsum()
    
    # Calculate capital requirement metrics
    lowest_cash_balance = ending_cash.min()
    cash_injection_required = max(0, -lowest_cash_balance)
    lowest_cash_period = int(ending_cash.idxmin())
    recommended_starting_cash = round(cash_injection_required * 1.10, 0)
    
    # Determine break-even period (first period where cash >= 0)
    break_even_period = None
    for i, val in enumerate(ending_cash):
        if val >= 0:
            break_even_period = i
            break
    
    # Calculate cash runway
    if lowest_cash_balance < 0:
        cash_runway_periods = lowest_cash_period
    else:
        cash_runway_periods = None
    
    # Diagnostic metadata for troubleshooting
    period_0_debug = {
        'beginning_ar_balance': starting_ar_balance,
        'beginning_ap_balance': starting_ap_balance if not (is_startup_like and starting_ap_balance == 0) else 0.0,
        'beginning_inventory_balance': starting_inventory_balance,
        'target_ar_balance': target_ar_balance.iloc[0] if len(target_ar_balance) > 0 else 0,
        'target_ap_balance': target_ap_balance.iloc[0] if len(target_ap_balance) > 0 else 0,
        'target_inventory_balance': target_inventory_balance.iloc[0] if len(target_inventory_balance) > 0 else 0,
        'is_startup_like': is_startup_like,
        'ap_change_period_0': ap_change.iloc[0] if len(ap_change) > 0 else 0,
        'working_capital_requirement': working_capital_requirement,
    }
    
    # Calculate required working capital for Period 0
    required_wc_calc = calculate_required_working_capital(
        revenue=revenue_total.iloc[0] if len(revenue_total) > 0 else 0.0,
        cogs=cogs.iloc[0] if len(cogs) > 0 else 0.0,
        ar_days=ar_days,
        ap_days=ap_days,
        inventory_days=inventory_days,
        days_in_period=days_in_period
    )
    
    # Calculate working capital coverage ratio
    # Coverage = Beginning Cash / Required Working Capital
    if required_wc_calc['required_wc'] > 0:
        working_capital_coverage = beginning_cash / required_wc_calc['required_wc']
    else:
        working_capital_coverage = None  # N/A when required WC is negative or zero
    
    # Capital requirement metrics
    capital_metrics = {
        'beginning_cash': beginning_cash,
        'lowest_cash_balance': lowest_cash_balance,
        'cash_injection_required': cash_injection_required,
        'lowest_cash_period': lowest_cash_period,
        'recommended_starting_cash': recommended_starting_cash,
        'break_even_period': break_even_period,
        'cash_runway_periods': cash_runway_periods,
        'required_working_capital': required_wc_calc['required_wc'],
        'required_wc_ar': required_wc_calc['ar'],
        'required_wc_ap': required_wc_calc['ap'],
        'required_wc_inventory': required_wc_calc['inventory'],
        'working_capital_coverage': working_capital_coverage,
        'working_capital_source': working_capital_source,
    }
    
    result_df = pd.DataFrame({
        'net_income': net_income,
        'ar_change': ar_change,
        'ap_change': ap_change,
        'inventory_change': inventory_change,
        'operating_cash_flow': operating_cash_flow,
        'financing_cash_flow': financing_cash_flow,
        'owner_distribution': owner_dist,
        'net_cash_flow': net_cash_flow,
        'ending_cash': ending_cash
    })
    
    # Attach metadata as attributes
    result_df.attrs['period_0_debug'] = period_0_debug
    result_df.attrs['capital_metrics'] = capital_metrics
    
    return result_df


def build_pnl_statement(revenue_total, cogs, direct_payroll, indirect_payroll, opex_total, interest_expense, 
                        annual_depreciation, tax_rate, time_mode, periods):
    """
    Build Profit & Loss statement with depreciation and taxes (A+ architecture).
    
    Args:
        revenue_total: Series of total revenue per period
        cogs: Series of COGS per period (materials only)
        direct_payroll: Series of direct payroll per period (flows to COGS)
        indirect_payroll: Series of indirect payroll per period (flows to Opex)
        opex_total: Series of total opex per period
        interest_expense: Series of interest expense per period
        annual_depreciation: Annual depreciation amount
        tax_rate: Corporate tax rate (e.g., 0.25 for 25%)
        time_mode: 'monthly' or 'annual'
        periods: Number of periods
    
    Returns:
        DataFrame with P&L line items including taxes
    """
    total_cogs = cogs + direct_payroll
    gross_profit = revenue_total - total_cogs
    operating_expenses = indirect_payroll + opex_total
    ebitda = gross_profit - operating_expenses
    
    if time_mode == 'monthly':
        depreciation_per_period = annual_depreciation / 12
    else:
        depreciation_per_period = annual_depreciation
    
    depreciation = pd.Series([depreciation_per_period] * periods, index=revenue_total.index)
    
    ebit = ebitda - depreciation
    pre_tax_income = ebit - interest_expense
    
    taxes = np.maximum(0, pre_tax_income * tax_rate)
    
    net_income = pre_tax_income - taxes
    
    return pd.DataFrame({
        'revenue': revenue_total,
        'cogs_materials': cogs,
        'cogs_direct_labor': direct_payroll,
        'cogs_total': total_cogs,
        'gross_profit': gross_profit,
        'indirect_payroll': indirect_payroll,
        'opex': opex_total,
        'operating_expenses': operating_expenses,
        'ebitda': ebitda,
        'depreciation': depreciation,
        'ebit': ebit,
        'interest': interest_expense,
        'pre_tax_income': pre_tax_income,
        'taxes': taxes,
        'net_income': net_income
    })


def calculate_kpis(income_statement, cash_flow_statement, loan_schedule, pnl_statement=None, 
                   opex_df=None, owner_comp_config=None, time_mode='monthly'):
    """
    Calculate key performance indicators including DSCR and break-even.
    
    Args:
        income_statement: DataFrame from build_income_statement
        cash_flow_statement: DataFrame from build_cash_flow_statement
        loan_schedule: DataFrame from calculate_loan_schedule
        pnl_statement: Optional DataFrame from build_pnl_statement
        opex_df: Optional DataFrame from calculate_opex (for break-even)
        owner_comp_config: Optional dict with owner compensation config
        time_mode: 'monthly' or 'annual'
    
    Returns:
        DataFrame with KPIs per period
    """
    from .underwriting import calculate_dscr, calculate_contribution_margin, calculate_break_even_revenue
    
    ebitda = income_statement['ebitda']
    debt_service = loan_schedule['payment']
    
    dscr = calculate_dscr(ebitda, debt_service, time_mode)
    
    kpi_data = {
        'ebitda': ebitda,
        'debt_service': debt_service,
        'dscr': dscr,
        'ending_cash': cash_flow_statement['ending_cash']
    }
    
    if pnl_statement is not None:
        kpi_data['net_income'] = pnl_statement['net_income']
        kpi_data['taxes'] = pnl_statement['taxes']
        
        revenue = pnl_statement['revenue']
        gross_profit = pnl_statement['gross_profit']
        ebitda_series = pnl_statement['ebitda']
        operating_expenses = pnl_statement['operating_expenses']
        
        # Calculate margins using safe_divide helper
        net_margin = pd.Series(0.0, index=revenue.index)
        gross_margin = pd.Series(0.0, index=revenue.index)
        ebitda_margin = pd.Series(0.0, index=revenue.index)
        overhead_load = pd.Series(0.0, index=revenue.index)
        payroll_pct_revenue = pd.Series(0.0, index=revenue.index)
        contribution_margin = pd.Series(0.0, index=revenue.index)
        
        for i in revenue.index:
            # Use safe_divide for all margin calculations
            net_margin.iloc[i] = calculate_margin(pnl_statement['net_income'].iloc[i], revenue.iloc[i])
            gross_margin.iloc[i] = calculate_margin(gross_profit.iloc[i], revenue.iloc[i])
            ebitda_margin.iloc[i] = calculate_margin(ebitda_series.iloc[i], revenue.iloc[i])
            overhead_load.iloc[i] = calculate_margin(operating_expenses.iloc[i], revenue.iloc[i])
            
            total_payroll = pnl_statement['cogs_direct_labor'].iloc[i] + pnl_statement['indirect_payroll'].iloc[i]
            payroll_pct_revenue.iloc[i] = calculate_margin(total_payroll, revenue.iloc[i])
            
            # Contribution margin = (Gross Profit - Indirect Payroll) / Revenue
            # This represents contribution after variable costs and before fixed overhead
            contribution = gross_profit.iloc[i] - pnl_statement['indirect_payroll'].iloc[i]
            contribution_margin.iloc[i] = calculate_margin(contribution, revenue.iloc[i])
        
        kpi_data['net_margin'] = net_margin
        kpi_data['gross_margin'] = gross_margin
        kpi_data['ebitda_margin'] = ebitda_margin
        kpi_data['overhead_load'] = overhead_load
        kpi_data['payroll_pct_revenue'] = payroll_pct_revenue
        kpi_data['contribution_margin'] = contribution_margin
        
        if opex_df is not None and owner_comp_config is not None:
            variable_costs = pnl_statement['cogs_total']
            if 'variable_total' in opex_df.columns:
                variable_costs = variable_costs + opex_df['variable_total']
            
            contrib_margin_series = calculate_contribution_margin(revenue, variable_costs)
            avg_contrib_margin = contrib_margin_series.mean()
            
            if time_mode == 'monthly':
                annual_indirect_payroll = pnl_statement['indirect_payroll'].sum()
                annual_fixed_opex = opex_df['fixed_total'].sum() if 'fixed_total' in opex_df.columns else 0
                annual_semi_fixed_opex = opex_df['semi_fixed_total'].sum() if 'semi_fixed_total' in opex_df.columns else 0
                annual_debt_service = debt_service.sum()
            else:
                annual_indirect_payroll = pnl_statement['indirect_payroll'].iloc[0] if len(pnl_statement) > 0 else 0
                annual_fixed_opex = opex_df['fixed_total'].iloc[0] if 'fixed_total' in opex_df.columns and len(opex_df) > 0 else 0
                annual_semi_fixed_opex = opex_df['semi_fixed_total'].iloc[0] if 'semi_fixed_total' in opex_df.columns and len(opex_df) > 0 else 0
                annual_debt_service = debt_service.iloc[0] if len(debt_service) > 0 else 0
            
            owner_salary_annual = owner_comp_config.get('amount', 0.0)
            
            break_even_rev = calculate_break_even_revenue(
                annual_indirect_payroll,
                annual_fixed_opex,
                annual_semi_fixed_opex,
                owner_salary_annual,
                annual_debt_service,
                avg_contrib_margin,
                time_mode
            )
            
            kpi_data['break_even_revenue'] = pd.Series([break_even_rev] * len(revenue), index=revenue.index)
            kpi_data['contribution_margin_pct'] = contrib_margin_series
            kpi_data['fixed_cost_base'] = pd.Series([annual_indirect_payroll + annual_fixed_opex + annual_semi_fixed_opex + owner_salary_annual + annual_debt_service] * len(revenue), index=revenue.index)
    
    return pd.DataFrame(kpi_data)
