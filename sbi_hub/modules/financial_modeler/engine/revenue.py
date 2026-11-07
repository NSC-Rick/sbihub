import pandas as pd
import numpy as np


def calculate_revenue(revenue_streams, time_mode, periods, seasonality=None, startup_ramp_months=0):
    """
    Calculate revenue for multiple streams over time.
    
    Args:
        revenue_streams: List of dicts with keys: name, price, volume, growth_rate, cogs_override
        time_mode: 'monthly' or 'annual'
        periods: Number of periods
        seasonality: Optional dict with keys: enabled, mode, custom_weights
        startup_ramp_months: Number of months to ramp from 0% to 100% revenue (default: 0 = disabled)
    
    Returns:
        DataFrame with period index and column per revenue stream plus total
    """
    if not revenue_streams:
        df = pd.DataFrame({'period': range(periods), 'total': [0] * periods})
        return df.set_index('period')
    
    revenue_data = {'period': range(periods)}
    
    # Get seasonality weights
    seasonal_weights = None
    if seasonality and seasonality.get('enabled') and time_mode == 'monthly':
        if seasonality['mode'] == 'Retail Preset':
            # Retail preset weights
            seasonal_weights = [6.5, 6.0, 7.5, 8.0, 8.5, 9.0, 9.5, 9.0, 8.0, 9.5, 11.0, 17.5]
        elif seasonality['mode'] == 'Custom':
            seasonal_weights = seasonality.get('custom_weights', [8.33] * 12)
        
        # Normalize to ensure sum = 100
        if seasonal_weights:
            total = sum(seasonal_weights)
            if total > 0:
                seasonal_weights = [w / total * 100 for w in seasonal_weights]
    
    for stream in revenue_streams:
        name = stream['name']
        price = stream['price']
        initial_volume = stream['volume']
        growth_rate = stream['growth_rate']
        
        revenues = []
        for period in range(periods):
            if time_mode == 'monthly':
                monthly_growth = (1 + growth_rate) ** (1/12) - 1
                volume = initial_volume * (1 + monthly_growth) ** period
            else:
                volume = initial_volume * (1 + growth_rate) ** period
            
            base_revenue = price * volume
            
            # Apply seasonality if enabled (monthly mode only)
            if seasonal_weights and time_mode == 'monthly':
                month_index = period % 12
                # Seasonal weight is percentage of annual revenue
                # Convert to monthly multiplier: weight / (100/12) = weight / 8.333...
                seasonal_multiplier = seasonal_weights[month_index] / (100 / 12)
                base_revenue *= seasonal_multiplier
            
            # Apply startup ramp if enabled (monthly mode only)
            if startup_ramp_months > 0 and time_mode == 'monthly':
                ramp_factor = min(1.0, (period + 1) / startup_ramp_months)
                base_revenue *= ramp_factor
            
            revenues.append(base_revenue)
        
        revenue_data[name] = revenues
    
    df = pd.DataFrame(revenue_data)
    df['total'] = df.drop('period', axis=1).sum(axis=1)
    
    return df.set_index('period')


def calculate_cogs(revenue_df, revenue_streams, global_cogs_pct, time_mode='monthly', cogs_improvement_pct=0.0):
    """
    Calculate COGS based on revenue with optional efficiency improvement.
    
    Args:
        revenue_df: DataFrame from calculate_revenue
        revenue_streams: List of revenue stream dicts (with optional cogs_override)
        global_cogs_pct: Default COGS percentage (e.g., 0.30 for 30%)
        time_mode: 'monthly' or 'annual'
        cogs_improvement_pct: Annual COGS improvement percentage (e.g., 2.0 for 2% per year)
    
    Returns:
        Series with COGS per period
    """
    cogs = pd.Series(0.0, index=revenue_df.index)
    
    for stream in revenue_streams:
        name = stream['name']
        cogs_override = stream.get('cogs_override')
        base_cogs_pct = cogs_override if cogs_override is not None else global_cogs_pct
        
        if name in revenue_df.columns:
            # Apply COGS efficiency improvement over time
            for period in revenue_df.index:
                if cogs_improvement_pct > 0:
                    # Calculate year index
                    if time_mode == 'monthly':
                        year_index = period / 12
                    else:
                        year_index = period
                    
                    # Apply compound improvement: adjusted_cogs = base_cogs * (1 - improvement_rate) ** year_index
                    improvement_rate = cogs_improvement_pct / 100.0
                    adjusted_cogs_pct = base_cogs_pct * ((1 - improvement_rate) ** year_index)
                else:
                    adjusted_cogs_pct = base_cogs_pct
                
                cogs.iloc[period] += revenue_df[name].iloc[period] * adjusted_cogs_pct
    
    return cogs
