import pandas as pd
import numpy as np


def calculate_payroll(payroll_roles, time_mode, periods):
    """
    Calculate payroll expenses over time with direct/indirect classification.
    
    Args:
        payroll_roles: List of dicts with keys: role, headcount, pay_type, rate, hours_per_week, 
                       annual_raise_pct, payroll_tax_pct, benefits_pct, role_type ('direct' or 'indirect')
        time_mode: 'monthly' or 'annual'
        periods: Number of periods
    
    Returns:
        DataFrame with period index and columns:
            - direct_wages, direct_taxes, direct_benefits, direct_total (flows to COGS)
            - indirect_wages, indirect_taxes, indirect_benefits, indirect_total (flows to Opex)
            - total (all payroll)
    """
    if not payroll_roles:
        return pd.DataFrame({
            'period': range(periods),
            'direct_wages': [0] * periods,
            'direct_taxes': [0] * periods,
            'direct_benefits': [0] * periods,
            'direct_total': [0] * periods,
            'indirect_wages': [0] * periods,
            'indirect_taxes': [0] * periods,
            'indirect_benefits': [0] * periods,
            'indirect_total': [0] * periods,
            'total': [0] * periods
        }).set_index('period')
    
    direct_wages = pd.Series(0.0, index=range(periods))
    direct_taxes = pd.Series(0.0, index=range(periods))
    direct_benefits = pd.Series(0.0, index=range(periods))
    
    indirect_wages = pd.Series(0.0, index=range(periods))
    indirect_taxes = pd.Series(0.0, index=range(periods))
    indirect_benefits = pd.Series(0.0, index=range(periods))
    
    for role in payroll_roles:
        headcount = role['headcount']
        pay_type = role['pay_type']
        rate = role['rate']
        hours_per_week = role.get('hours_per_week', 40)
        annual_raise_pct = role['annual_raise_pct']
        payroll_tax_pct = role['payroll_tax_pct']
        benefits_pct = role['benefits_pct']
        role_type = role.get('role_type', 'indirect')
        
        for period in range(periods):
            if time_mode == 'monthly':
                years_elapsed = period / 12
                raise_multiplier = (1 + annual_raise_pct) ** years_elapsed
                
                if pay_type == 'hourly':
                    monthly_hours = hours_per_week * 52 / 12
                    period_wages = headcount * rate * monthly_hours * raise_multiplier
                else:
                    period_wages = headcount * rate / 12 * raise_multiplier
            else:
                years_elapsed = period
                raise_multiplier = (1 + annual_raise_pct) ** years_elapsed
                
                if pay_type == 'hourly':
                    annual_hours = hours_per_week * 52
                    period_wages = headcount * rate * annual_hours * raise_multiplier
                else:
                    period_wages = headcount * rate * raise_multiplier
            
            period_taxes = period_wages * payroll_tax_pct
            period_benefits = period_wages * benefits_pct
            
            if role_type == 'direct':
                direct_wages[period] += period_wages
                direct_taxes[period] += period_taxes
                direct_benefits[period] += period_benefits
            else:
                indirect_wages[period] += period_wages
                indirect_taxes[period] += period_taxes
                indirect_benefits[period] += period_benefits
    
    direct_total = direct_wages + direct_taxes + direct_benefits
    indirect_total = indirect_wages + indirect_taxes + indirect_benefits
    total = direct_total + indirect_total
    
    return pd.DataFrame({
        'direct_wages': direct_wages,
        'direct_taxes': direct_taxes,
        'direct_benefits': direct_benefits,
        'direct_total': direct_total,
        'indirect_wages': indirect_wages,
        'indirect_taxes': indirect_taxes,
        'indirect_benefits': indirect_benefits,
        'indirect_total': indirect_total,
        'total': total
    })
