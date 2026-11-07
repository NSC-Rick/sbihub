import pandas as pd
from .revenue import calculate_revenue, calculate_cogs
from .payroll import calculate_payroll
from .opex import calculate_opex
from .loan import calculate_loan_schedule
from .statements import build_income_statement, build_cash_flow_statement, build_pnl_statement, calculate_kpis
from .underwriting import apply_owner_compensation_to_payroll, calculate_owner_distribution


def build_model(model_inputs):
    """
    Main engine entrypoint. Build complete financial model from inputs.
    
    Args:
        model_inputs: Dict containing all model parameters:
            - time_mode: 'monthly' or 'annual'
            - periods: Number of periods (60 for monthly, 5 for annual)
            - revenue_streams: List of revenue stream dicts
            - global_cogs_pct: Default COGS percentage
            - payroll_roles: List of payroll role dicts
            - opex_items: List of opex item dicts
            - loan_principal: Loan amount
            - loan_annual_rate: Annual interest rate
            - loan_term_months: Loan term in months
            - loan_start_period: Period when loan starts
            - ar_days: Accounts receivable days
            - ap_days: Accounts payable days
            - inventory_days: Inventory days
            - tax_rate: Corporate tax rate (e.g., 0.25 for 25%)
            - annual_depreciation: Annual depreciation amount
    
    Returns:
        Dict with keys:
            - revenue_df: Revenue DataFrame
            - cogs: COGS Series
            - payroll_df: Payroll DataFrame
            - opex_df: Opex DataFrame
            - loan_schedule: Loan schedule DataFrame
            - income_statement: Income statement DataFrame (operating only)
            - pnl_statement: P&L statement DataFrame (with depreciation and taxes)
            - cash_flow_statement: Cash flow statement DataFrame
            - kpis: KPIs DataFrame
    """
    time_mode = model_inputs['time_mode']
    periods = model_inputs['periods']
    
    revenue_df = calculate_revenue(
        model_inputs['revenue_streams'],
        time_mode,
        periods,
        model_inputs.get('seasonality'),
        model_inputs.get('startup_ramp_months', 0)
    )
    
    cogs = calculate_cogs(
        revenue_df,
        model_inputs['revenue_streams'],
        model_inputs['global_cogs_pct'],
        time_mode,
        model_inputs.get('cogs_improvement_pct', 0.0)
    )
    
    owner_comp_config = model_inputs.get('owner_compensation', {'mode': 'distribution', 'amount': 0.0})
    
    payroll_roles_with_owner = apply_owner_compensation_to_payroll(
        model_inputs['payroll_roles'],
        owner_comp_config,
        time_mode
    )
    
    payroll_df = calculate_payroll(
        payroll_roles_with_owner,
        time_mode,
        periods
    )
    
    opex_df = calculate_opex(
        model_inputs['opex_items'],
        time_mode,
        periods,
        revenue_df['total']
    )
    
    loan_schedule = calculate_loan_schedule(
        model_inputs['loan_principal'],
        model_inputs['loan_annual_rate'],
        model_inputs['loan_term_months'],
        model_inputs['loan_start_period'],
        time_mode,
        periods
    )
    
    income_statement = build_income_statement(
        revenue_df['total'],
        cogs,
        payroll_df['total'],
        opex_df['total'],
        loan_schedule['interest']
    )
    
    pnl_statement = build_pnl_statement(
        revenue_df['total'],
        cogs,
        payroll_df['direct_total'],
        payroll_df['indirect_total'],
        opex_df['total'],
        loan_schedule['interest'],
        model_inputs.get('annual_depreciation', 0.0),
        model_inputs.get('tax_rate', 0.25),
        time_mode,
        periods
    )
    
    owner_distribution = calculate_owner_distribution(
        owner_comp_config,
        time_mode,
        periods
    )
    
    # Extract working capital funding from capital stack
    working_capital_funding = 0.0
    if model_inputs.get('capital_stack', {}).get('enabled', False):
        working_capital_funding = (
            model_inputs['capital_stack']
            .get('uses', {})
            .get('working_capital', 0.0)
        )
    
    cash_flow_statement = build_cash_flow_statement(
        pnl_statement['net_income'],
        loan_schedule['principal'],
        loan_schedule['payment'],
        model_inputs['ar_days'],
        model_inputs['ap_days'],
        model_inputs['inventory_days'],
        revenue_df['total'],
        cogs,
        time_mode,
        owner_distribution,
        business_stage=model_inputs.get('business_stage', 'acquisition'),
        starting_ar_balance=model_inputs.get('starting_ar_balance', 0.0),
        starting_ap_balance=model_inputs.get('starting_ap_balance', 0.0),
        starting_inventory_balance=model_inputs.get('starting_inventory_balance', 0.0),
        capital_stack_enabled=model_inputs.get('capital_stack', {}).get('enabled', False),
        beginning_cash=working_capital_funding,
        model_mode=model_inputs.get('model_mode', 'startup'),
        working_capital_source=model_inputs.get('working_capital_source', 'buyer_injected')
    )
    
    kpis = calculate_kpis(
        income_statement,
        cash_flow_statement,
        loan_schedule,
        pnl_statement,
        opex_df,
        owner_comp_config,
        time_mode
    )
    
    return {
        'revenue_df': revenue_df,
        'cogs': cogs,
        'payroll_df': payroll_df,
        'opex_df': opex_df,
        'loan_schedule': loan_schedule,
        'income_statement': income_statement,
        'pnl_statement': pnl_statement,
        'cash_flow_statement': cash_flow_statement,
        'kpis': kpis
    }
