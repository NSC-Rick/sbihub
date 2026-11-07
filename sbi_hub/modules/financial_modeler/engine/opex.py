import pandas as pd
import numpy as np


def calculate_opex(opex_items, time_mode, periods, revenue_total=None):
    """
    Calculate operating expenses over time with support for fixed, semi-fixed, and variable % revenue.
    
    Args:
        opex_items: List of dicts with keys:
            - name: Expense name
            - category: 'fixed', 'semi-fixed', or 'variable_pct_revenue'
            - amount: Initial amount (for fixed/semi-fixed) or percentage (for variable)
            - growth_rate: Annual growth rate (for fixed/semi-fixed only)
        time_mode: 'monthly' or 'annual'
        periods: Number of periods
        revenue_total: Series of total revenue per period (required for variable_pct_revenue items)
    
    Returns:
        DataFrame with period index and columns:
            - One column per opex item
            - fixed_total, semi_fixed_total, variable_total
            - total (all opex)
    """
    if not opex_items:
        return pd.DataFrame({
            'period': range(periods),
            'fixed_total': [0] * periods,
            'semi_fixed_total': [0] * periods,
            'variable_total': [0] * periods,
            'total': [0] * periods
        }).set_index('period')
    
    opex_data = {'period': range(periods)}
    fixed_total = pd.Series(0.0, index=range(periods))
    semi_fixed_total = pd.Series(0.0, index=range(periods))
    variable_total = pd.Series(0.0, index=range(periods))
    
    for item in opex_items:
        name = item['name']
        category = item.get('category', 'fixed')
        
        if category == 'variable_pct_revenue':
            pct = item['amount']
            if revenue_total is not None:
                expenses = revenue_total * pct
            else:
                expenses = pd.Series([0] * periods, index=range(periods))
            variable_total += expenses
        else:
            initial_amount = item['amount']
            growth_rate = item.get('growth_rate', 0.0)
            
            expenses = []
            for period in range(periods):
                if time_mode == 'monthly':
                    monthly_growth = (1 + growth_rate) ** (1/12) - 1
                    amount = initial_amount * (1 + monthly_growth) ** period
                else:
                    amount = initial_amount * (1 + growth_rate) ** period
                
                expenses.append(amount)
            
            expenses = pd.Series(expenses, index=range(periods))
            
            if category == 'semi-fixed':
                semi_fixed_total += expenses
            else:
                fixed_total += expenses
        
        opex_data[name] = expenses
    
    total = fixed_total + semi_fixed_total + variable_total
    
    df = pd.DataFrame(opex_data)
    df['fixed_total'] = fixed_total
    df['semi_fixed_total'] = semi_fixed_total
    df['variable_total'] = variable_total
    df['total'] = total
    
    return df.set_index('period')
