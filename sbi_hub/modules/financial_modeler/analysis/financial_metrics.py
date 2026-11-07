"""
Canonical financial metrics engine for DSCR, cash flow, and insights calculations.

This module provides a single source of truth for all financial metrics calculations
to ensure consistency across DSCR displays, insights flags, and underwriting analysis.
"""

import pandas as pd
import numpy as np


def compute_financial_metrics(
    income_statement,
    cash_flow_statement,
    loan_schedule,
    owner_comp_config=None,
    time_mode='monthly'
):
    """
    Centralized financial metrics engine used by DSCR, Insights, and Underwriting modules.
    
    This function computes all key financial metrics from a single canonical source,
    ensuring consistency across the application.
    
    Args:
        income_statement: DataFrame from build_income_statement with columns:
            - ebitda: EBITDA per period
            - net_income: Net income per period
            - revenue: Revenue per period
        cash_flow_statement: DataFrame from build_cash_flow_statement with columns:
            - operating_cash_flow: Operating cash flow per period
            - net_cash_flow: Net cash flow per period
            - ending_cash: Ending cash balance per period
        loan_schedule: DataFrame from calculate_loan_schedule with columns:
            - payment: Total debt service (principal + interest) per period
            - principal: Principal payment per period
            - interest: Interest payment per period
        owner_comp_config: Optional dict with owner compensation config:
            - mode: 'payroll' or 'distribution'
            - amount: Annual amount
        time_mode: 'monthly' or 'annual'
    
    Returns:
        Dict with canonical financial metrics:
            - dscr_series: DSCR per period (Series)
            - avg_dscr: Average DSCR across all periods (float)
            - current_dscr: DSCR for first period (float or None)
            - operating_cash_flow: Operating cash flow per period (Series)
            - debt_service: Total debt service per period (Series)
            - cash_after_debt: Cash after debt service per period (Series)
            - cash_after_owner: Cash after debt and owner comp per period (Series)
            - owner_compensation: Owner compensation per period (Series)
            - ebitda: EBITDA per period (Series)
            - net_income: Net income per period (Series)
            - ending_cash: Ending cash balance per period (Series)
    """
    # Extract core financial components
    operating_cash_flow = cash_flow_statement['operating_cash_flow']
    debt_service = loan_schedule['payment']
    ebitda = income_statement['ebitda']
    net_income = income_statement['net_income']
    ending_cash = cash_flow_statement['ending_cash']
    
    # Calculate owner compensation per period
    if owner_comp_config and owner_comp_config.get('mode') == 'distribution':
        annual_amount = owner_comp_config.get('amount', 0.0)
        if time_mode == 'monthly':
            owner_comp_per_period = annual_amount / 12
        else:
            owner_comp_per_period = annual_amount
        owner_compensation = pd.Series([owner_comp_per_period] * len(operating_cash_flow), 
                                      index=operating_cash_flow.index)
    else:
        # If payroll mode, owner comp is already in payroll expenses
        owner_compensation = pd.Series([0.0] * len(operating_cash_flow), 
                                      index=operating_cash_flow.index)
    
    # Calculate DSCR using EBITDA (industry standard)
    # DSCR = EBITDA / Total Debt Service
    dscr_series = pd.Series(None, index=ebitda.index, dtype='object')
    for i in ebitda.index:
        if debt_service.iloc[i] > 0:
            dscr_series.iloc[i] = ebitda.iloc[i] / debt_service.iloc[i]
        else:
            dscr_series.iloc[i] = None
    
    # Calculate average DSCR (excluding None values)
    valid_dscr = [x for x in dscr_series if x is not None]
    avg_dscr = sum(valid_dscr) / len(valid_dscr) if valid_dscr else None
    
    # Get current (first period) DSCR
    current_dscr = dscr_series.iloc[0] if len(dscr_series) > 0 else None
    
    # Calculate cash after debt and owner compensation
    cash_after_debt = operating_cash_flow - debt_service
    cash_after_owner = cash_after_debt - owner_compensation
    
    # Return canonical metrics
    metrics = {
        # DSCR metrics
        'dscr_series': dscr_series,
        'avg_dscr': avg_dscr,
        'current_dscr': current_dscr,
        
        # Cash flow metrics
        'operating_cash_flow': operating_cash_flow,
        'debt_service': debt_service,
        'cash_after_debt': cash_after_debt,
        'cash_after_owner': cash_after_owner,
        'owner_compensation': owner_compensation,
        
        # Income metrics
        'ebitda': ebitda,
        'net_income': net_income,
        'ending_cash': ending_cash,
        
        # Aggregate metrics
        'total_debt_service': debt_service.sum() if time_mode == 'monthly' else debt_service.iloc[0] if len(debt_service) > 0 else 0,
        'avg_operating_cash_flow': operating_cash_flow.mean(),
        'avg_cash_after_debt': cash_after_debt.mean(),
        'avg_cash_after_owner': cash_after_owner.mean()
    }
    
    return metrics


def get_dscr_for_period(metrics, period_index=0):
    """
    Get DSCR for a specific period from canonical metrics.
    
    Args:
        metrics: Dict from compute_financial_metrics()
        period_index: Period index (default 0 for first period)
    
    Returns:
        Float DSCR value or None if no debt
    """
    dscr_series = metrics['dscr_series']
    if period_index < len(dscr_series):
        return dscr_series.iloc[period_index]
    return None


def get_cash_metrics_for_period(metrics, period_index=0):
    """
    Get cash flow metrics for a specific period from canonical metrics.
    
    Args:
        metrics: Dict from compute_financial_metrics()
        period_index: Period index (default 0 for first period)
    
    Returns:
        Dict with cash metrics for the period:
            - operating_cash_flow: Operating cash flow
            - cash_after_debt: Cash after debt service
            - cash_after_owner: Cash after debt and owner comp
            - debt_service: Debt service payment
    """
    return {
        'operating_cash_flow': metrics['operating_cash_flow'].iloc[period_index],
        'cash_after_debt': metrics['cash_after_debt'].iloc[period_index],
        'cash_after_owner': metrics['cash_after_owner'].iloc[period_index],
        'debt_service': metrics['debt_service'].iloc[period_index]
    }


def validate_metrics_consistency(metrics):
    """
    Validate that financial metrics are internally consistent.
    
    Args:
        metrics: Dict from compute_financial_metrics()
    
    Returns:
        Tuple (is_valid, error_messages)
    """
    errors = []
    
    # Check that cash_after_debt = operating_cash_flow - debt_service
    expected_cash_after_debt = metrics['operating_cash_flow'] - metrics['debt_service']
    if not metrics['cash_after_debt'].equals(expected_cash_after_debt):
        errors.append("Cash after debt calculation inconsistent")
    
    # Check that cash_after_owner = cash_after_debt - owner_compensation
    expected_cash_after_owner = metrics['cash_after_debt'] - metrics['owner_compensation']
    if not metrics['cash_after_owner'].equals(expected_cash_after_owner):
        errors.append("Cash after owner calculation inconsistent")
    
    # Check DSCR calculation for periods with debt
    for i in range(len(metrics['dscr_series'])):
        if metrics['debt_service'].iloc[i] > 0:
            expected_dscr = metrics['ebitda'].iloc[i] / metrics['debt_service'].iloc[i]
            actual_dscr = metrics['dscr_series'].iloc[i]
            if actual_dscr is not None and abs(expected_dscr - actual_dscr) > 0.01:
                errors.append(f"DSCR calculation inconsistent at period {i}")
                break
    
    return (len(errors) == 0, errors)
