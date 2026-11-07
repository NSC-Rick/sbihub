import pandas as pd
import numpy as np


def calculate_loan_schedule(principal, annual_rate, term_months, start_period, time_mode, periods):
    """
    Calculate loan amortization schedule.
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (e.g., 0.06 for 6%)
        term_months: Loan term in months
        start_period: Period when loan starts (0-indexed)
        time_mode: 'monthly' or 'annual'
        periods: Total number of periods in model
    
    Returns:
        DataFrame with columns: period, beginning_balance, payment, interest, principal, ending_balance
    """
    if principal <= 0 or annual_rate < 0 or term_months <= 0:
        return pd.DataFrame({
            'period': range(periods),
            'beginning_balance': [0] * periods,
            'payment': [0] * periods,
            'interest': [0] * periods,
            'principal': [0] * periods,
            'ending_balance': [0] * periods
        })
    
    if time_mode == 'monthly':
        monthly_rate = annual_rate / 12
        payment_periods = term_months
        payment = principal * (monthly_rate * (1 + monthly_rate)**payment_periods) / ((1 + monthly_rate)**payment_periods - 1)
        
        schedule = []
        balance = principal
        
        for period in range(periods):
            if period < start_period:
                schedule.append({
                    'period': period,
                    'beginning_balance': 0,
                    'payment': 0,
                    'interest': 0,
                    'principal': 0,
                    'ending_balance': 0
                })
            elif period < start_period + payment_periods:
                interest = balance * monthly_rate
                principal_payment = payment - interest
                ending_balance = balance - principal_payment
                
                schedule.append({
                    'period': period,
                    'beginning_balance': balance,
                    'payment': payment,
                    'interest': interest,
                    'principal': principal_payment,
                    'ending_balance': max(0, ending_balance)
                })
                balance = max(0, ending_balance)
            else:
                schedule.append({
                    'period': period,
                    'beginning_balance': 0,
                    'payment': 0,
                    'interest': 0,
                    'principal': 0,
                    'ending_balance': 0
                })
    else:
        annual_rate_effective = annual_rate
        payment_years = int(np.ceil(term_months / 12))
        payment = principal * (annual_rate_effective * (1 + annual_rate_effective)**payment_years) / ((1 + annual_rate_effective)**payment_years - 1)
        
        schedule = []
        balance = principal
        
        for period in range(periods):
            if period < start_period:
                schedule.append({
                    'period': period,
                    'beginning_balance': 0,
                    'payment': 0,
                    'interest': 0,
                    'principal': 0,
                    'ending_balance': 0
                })
            elif period < start_period + payment_years:
                interest = balance * annual_rate_effective
                principal_payment = payment - interest
                ending_balance = balance - principal_payment
                
                schedule.append({
                    'period': period,
                    'beginning_balance': balance,
                    'payment': payment,
                    'interest': interest,
                    'principal': principal_payment,
                    'ending_balance': max(0, ending_balance)
                })
                balance = max(0, ending_balance)
            else:
                schedule.append({
                    'period': period,
                    'beginning_balance': 0,
                    'payment': 0,
                    'interest': 0,
                    'principal': 0,
                    'ending_balance': 0
                })
    
    return pd.DataFrame(schedule)
