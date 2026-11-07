import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from sbi_hub.modules.financial_modeler.engine.loan import calculate_loan_schedule


def test_loan_amortization_monthly():
    """Test monthly loan amortization calculation."""
    principal = 100000
    annual_rate = 0.06
    term_months = 36  # Match forecast period
    start_period = 0
    time_mode = 'monthly'
    periods = 36
    
    schedule = calculate_loan_schedule(
        principal, annual_rate, term_months, start_period, time_mode, periods
    )
    
    assert len(schedule) == periods
    assert schedule['beginning_balance'].iloc[0] == principal
    assert schedule['ending_balance'].iloc[-1] < 1.0
    
    total_interest = schedule['interest'].sum()
    total_principal = schedule['principal'].sum()
    
    assert abs(total_principal - principal) < 1.0
    assert total_interest > 0


def test_loan_amortization_annual():
    """Test annual loan amortization calculation."""
    principal = 100000
    annual_rate = 0.06
    term_months = 36  # 3 years
    start_period = 0
    time_mode = 'annual'
    periods = 3
    
    schedule = calculate_loan_schedule(
        principal, annual_rate, term_months, start_period, time_mode, periods
    )
    
    assert len(schedule) == periods
    assert schedule['beginning_balance'].iloc[0] == principal
    assert schedule['ending_balance'].iloc[-1] < 1.0


def test_loan_delayed_start():
    """Test loan with delayed start period."""
    principal = 50000
    annual_rate = 0.05
    term_months = 36
    start_period = 12
    time_mode = 'monthly'
    periods = 36
    
    schedule = calculate_loan_schedule(
        principal, annual_rate, term_months, start_period, time_mode, periods
    )
    
    assert schedule['beginning_balance'].iloc[0] == 0
    assert schedule['beginning_balance'].iloc[11] == 0
    assert schedule['beginning_balance'].iloc[12] == principal
    
    for i in range(start_period):
        assert schedule['payment'].iloc[i] == 0


def test_loan_zero_principal():
    """Test loan with zero principal."""
    schedule = calculate_loan_schedule(0, 0.06, 36, 0, 'monthly', 36)
    
    assert len(schedule) == 36
    assert schedule['payment'].sum() == 0
    assert schedule['interest'].sum() == 0


def test_loan_payment_consistency():
    """Test that loan payments are consistent (except last payment)."""
    principal = 100000
    annual_rate = 0.06
    term_months = 36  # Match forecast period
    start_period = 0
    time_mode = 'monthly'
    periods = 36
    
    schedule = calculate_loan_schedule(
        principal, annual_rate, term_months, start_period, time_mode, periods
    )
    
    active_payments = schedule[schedule['payment'] > 0]['payment']
    
    if len(active_payments) > 1:
        payment_std = active_payments.iloc[:-1].std()
        assert payment_std < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
