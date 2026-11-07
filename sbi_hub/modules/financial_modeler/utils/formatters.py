"""
Formatting utilities for safe display of numeric values.

This module provides None-safe formatting functions to prevent
Streamlit/Pandas formatting crashes when values are None, NaN, or missing.
"""

import pandas as pd
import numpy as np


def safe_number(value, fmt="{:,.2f}", prefix="", suffix="", placeholder="—"):
    """
    Safely format a numeric value with None/NaN handling.
    
    Args:
        value: The value to format (int, float, None, NaN, etc.)
        fmt: Format string (default: "{:,.2f}" for comma-separated decimals)
        prefix: String to prepend (e.g., "$" for currency)
        suffix: String to append (e.g., "%" for percentages)
        placeholder: String to display for None/NaN values (default: "—")
    
    Returns:
        Formatted string or placeholder
    
    Examples:
        >>> safe_number(1234.56, "{:,.2f}", "$")
        '$1,234.56'
        
        >>> safe_number(None)
        '—'
        
        >>> safe_number(0.85, "{:.2f}")
        '0.85'
        
        >>> safe_number(float('nan'))
        '—'
    """
    # Handle None
    if value is None:
        return placeholder
    
    # Handle NaN (pandas/numpy)
    if pd.isna(value):
        return placeholder
    
    # Try to format numeric values
    try:
        if isinstance(value, (int, float, np.integer, np.floating)):
            # Check if it's NaN using math (for numpy types)
            if np.isnan(value):
                return placeholder
            return f"{prefix}{fmt.format(value)}{suffix}"
        
        # If it's already a string, return as-is
        if isinstance(value, str):
            return value
        
        # For other types, try to convert and format
        numeric_value = float(value)
        if np.isnan(numeric_value):
            return placeholder
        return f"{prefix}{fmt.format(numeric_value)}{suffix}"
        
    except (ValueError, TypeError, AttributeError):
        # If conversion or formatting fails, return placeholder
        return placeholder


def safe_currency(value, decimals=2, placeholder="—"):
    """
    Safely format a value as currency.
    
    Args:
        value: The value to format
        decimals: Number of decimal places (default: 2)
        placeholder: String to display for None/NaN values (default: "—")
    
    Returns:
        Formatted currency string or placeholder
    
    Examples:
        >>> safe_currency(1234.56)
        '$1,234.56'
        
        >>> safe_currency(None)
        '—'
        
        >>> safe_currency(1000, decimals=0)
        '$1,000'
    """
    fmt = f"{{:,.{decimals}f}}"
    return safe_number(value, fmt=fmt, prefix="$", placeholder=placeholder)


def safe_percentage(value, decimals=2, placeholder="—"):
    """
    Safely format a value as a percentage.
    
    Args:
        value: The value to format (as decimal, e.g., 0.85 for 85%)
        decimals: Number of decimal places (default: 2)
        placeholder: String to display for None/NaN values (default: "—")
    
    Returns:
        Formatted percentage string or placeholder
    
    Examples:
        >>> safe_percentage(0.8567)
        '85.67%'
        
        >>> safe_percentage(None)
        '—'
        
        >>> safe_percentage(1.25, decimals=0)
        '125%'
    """
    if value is None or pd.isna(value):
        return placeholder
    
    try:
        # Convert decimal to percentage
        percentage_value = float(value) * 100
        if np.isnan(percentage_value):
            return placeholder
        fmt = f"{{:,.{decimals}f}}"
        return safe_number(percentage_value, fmt=fmt, suffix="%", placeholder=placeholder)
    except (ValueError, TypeError, AttributeError):
        return placeholder


def safe_ratio(value, decimals=2, placeholder="—"):
    """
    Safely format a value as a ratio (e.g., DSCR).
    
    Args:
        value: The value to format
        decimals: Number of decimal places (default: 2)
        placeholder: String to display for None/NaN values (default: "—")
    
    Returns:
        Formatted ratio string or placeholder
    
    Examples:
        >>> safe_ratio(1.45)
        '1.45'
        
        >>> safe_ratio(None)
        '—'
        
        >>> safe_ratio(0.85, decimals=3)
        '0.850'
    """
    fmt = f"{{:.{decimals}f}}"
    return safe_number(value, fmt=fmt, placeholder=placeholder)


def safe_integer(value, placeholder="—"):
    """
    Safely format a value as an integer with comma separators.
    
    Args:
        value: The value to format
        placeholder: String to display for None/NaN values (default: "—")
    
    Returns:
        Formatted integer string or placeholder
    
    Examples:
        >>> safe_integer(1234567)
        '1,234,567'
        
        >>> safe_integer(None)
        '—'
        
        >>> safe_integer(1234.56)
        '1,235'
    """
    return safe_number(value, fmt="{:,.0f}", placeholder=placeholder)
