import pandas as pd
import numpy as np


def calculate_dscr(ebitda, debt_service, time_mode):
    """
    Calculate Debt Service Coverage Ratio (DSCR).
    
    Formula: DSCR = EBITDA / Total Debt Service
    
    Args:
        ebitda: Series of EBITDA per period
        debt_service: Series of total debt service (principal + interest) per period
        time_mode: 'monthly' or 'annual'
    
    Returns:
        Series of DSCR per period (None when debt service is 0)
    """
    dscr = pd.Series(None, index=ebitda.index, dtype='object')
    
    for i in ebitda.index:
        if debt_service.iloc[i] > 0:
            dscr.iloc[i] = ebitda.iloc[i] / debt_service.iloc[i]
        else:
            dscr.iloc[i] = None
    
    return dscr


def calculate_annual_dscr(ebitda, debt_service, time_mode, periods):
    """
    Calculate annual DSCR (aggregate monthly to annual if needed).
    
    Args:
        ebitda: Series of EBITDA per period
        debt_service: Series of total debt service per period
        time_mode: 'monthly' or 'annual'
        periods: Number of periods
    
    Returns:
        Float representing annual DSCR (None when debt service is 0)
    """
    if time_mode == 'monthly':
        annual_ebitda = ebitda.sum()
        annual_debt_service = debt_service.sum()
    else:
        annual_ebitda = ebitda.iloc[0] if len(ebitda) > 0 else 0
        annual_debt_service = debt_service.iloc[0] if len(debt_service) > 0 else 0
    
    if annual_debt_service > 0:
        return annual_ebitda / annual_debt_service
    else:
        return None


def calculate_contribution_margin(revenue, variable_costs):
    """
    Calculate contribution margin percentage.
    
    Formula: (Revenue - Variable Costs) / Revenue
    
    Args:
        revenue: Series of revenue per period
        variable_costs: Series of variable costs per period
    
    Returns:
        Series of contribution margin % per period
    """
    contribution_margin = pd.Series(0.0, index=revenue.index)
    
    for i in revenue.index:
        if revenue.iloc[i] > 0:
            contribution = revenue.iloc[i] - variable_costs.iloc[i]
            contribution_margin.iloc[i] = contribution / revenue.iloc[i]
        else:
            contribution_margin.iloc[i] = 0
    
    return contribution_margin


def calculate_break_even_revenue(
    indirect_payroll,
    fixed_opex,
    semi_fixed_opex,
    owner_salary_annual,
    annual_debt_service,
    contribution_margin_pct,
    time_mode
):
    """
    Calculate economic break-even revenue.
    
    Break-even must cover:
    - Indirect payroll
    - Fixed operating expenses
    - Semi-fixed operating expenses
    - Owner salary (always included)
    - Total annual debt service
    
    Formula: Break-Even Revenue = Fixed Cost Base / Contribution Margin %
    
    Args:
        indirect_payroll: Annual indirect payroll
        fixed_opex: Annual fixed operating expenses
        semi_fixed_opex: Annual semi-fixed operating expenses
        owner_salary_annual: Annual owner salary (always included)
        annual_debt_service: Annual debt service
        contribution_margin_pct: Contribution margin percentage
        time_mode: 'monthly' or 'annual'
    
    Returns:
        Float representing annual break-even revenue (or NaN if contribution margin <= 0)
    """
    fixed_cost_base = (
        indirect_payroll +
        fixed_opex +
        semi_fixed_opex +
        owner_salary_annual +
        annual_debt_service
    )
    
    if contribution_margin_pct > 0:
        break_even = fixed_cost_base / contribution_margin_pct
        return break_even
    else:
        return np.nan


def apply_owner_compensation_to_payroll(payroll_roles, owner_comp_config, time_mode):
    """
    Add owner compensation to payroll roles if mode is 'payroll'.
    
    Args:
        payroll_roles: List of payroll role dicts
        owner_comp_config: Dict with 'mode' and 'amount' keys
        time_mode: 'monthly' or 'annual'
    
    Returns:
        Updated list of payroll roles (with owner added if mode is 'payroll')
    """
    if owner_comp_config.get('mode') == 'payroll' and owner_comp_config.get('amount', 0) > 0:
        owner_role = {
            'role': 'Owner',
            'headcount': 1,
            'pay_type': 'salary',
            'rate': owner_comp_config['amount'],
            'hours_per_week': 40,
            'annual_raise_pct': 0.0,
            'payroll_tax_pct': 0.0765,
            'benefits_pct': 0.0,
            'role_type': 'indirect'
        }
        return payroll_roles + [owner_role]
    else:
        return payroll_roles


def calculate_owner_distribution(owner_comp_config, time_mode, periods):
    """
    Calculate owner distribution per period if mode is 'distribution'.
    
    Args:
        owner_comp_config: Dict with 'mode' and 'amount' keys
        time_mode: 'monthly' or 'annual'
        periods: Number of periods
    
    Returns:
        Series of owner distribution per period (total across all periods = annual amount)
    """
    if owner_comp_config.get('mode') == 'distribution' and owner_comp_config.get('amount', 0) > 0:
        annual_amount = owner_comp_config['amount']
        
        if time_mode == 'monthly':
            # Distribute annual amount across 12 months per year
            # For 60 months (5 years), total should be 5 × annual_amount
            per_period = annual_amount / 12
        else:
            # For annual mode, full amount per year
            per_period = annual_amount
        
        return pd.Series([per_period] * periods, index=range(periods))
    else:
        return pd.Series([0.0] * periods, index=range(periods))
