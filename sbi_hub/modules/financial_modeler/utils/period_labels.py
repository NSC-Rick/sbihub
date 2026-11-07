"""
Utility functions for generating calendar-based period labels.
Enhancement 2 - WPP Financial Modeler v1.1
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta


def generate_period_labels(start_month, start_year, num_periods, time_mode='monthly'):
    """
    Generate calendar-based period labels for financial statements.
    
    Args:
        start_month (int): Starting month (1-12)
        start_year (int): Starting year
        num_periods (int): Number of periods to generate
        time_mode (str): 'monthly' or 'annual'
    
    Returns:
        list: Period labels (e.g., ['Jan 2026', 'Feb 2026', ...])
    
    Examples:
        >>> generate_period_labels(1, 2026, 3, 'monthly')
        ['Jan 2026', 'Feb 2026', 'Mar 2026']
        
        >>> generate_period_labels(11, 2025, 3, 'monthly')
        ['Nov 2025', 'Dec 2025', 'Jan 2026']
        
        >>> generate_period_labels(1, 2026, 3, 'annual')
        ['2026', '2027', '2028']
    """
    labels = []
    
    if time_mode == 'annual':
        # Annual mode: just show years
        for i in range(num_periods):
            labels.append(str(start_year + i))
    else:
        # Monthly mode: show month abbreviation + year
        month_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        start_date = datetime(start_year, start_month, 1)
        
        for i in range(num_periods):
            current_date = start_date + relativedelta(months=i)
            month_name = month_abbr[current_date.month - 1]
            year = current_date.year
            labels.append(f"{month_name} {year}")
    
    return labels


def get_period_label(period_index, start_month, start_year, time_mode='monthly'):
    """
    Get a single period label for a given period index.
    
    Args:
        period_index (int): Zero-based period index
        start_month (int): Starting month (1-12)
        start_year (int): Starting year
        time_mode (str): 'monthly' or 'annual'
    
    Returns:
        str: Period label (e.g., 'Jan 2026')
    
    Examples:
        >>> get_period_label(0, 1, 2026, 'monthly')
        'Jan 2026'
        
        >>> get_period_label(13, 1, 2026, 'monthly')
        'Feb 2027'
    """
    if time_mode == 'annual':
        return str(start_year + period_index)
    else:
        month_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        start_date = datetime(start_year, start_month, 1)
        current_date = start_date + relativedelta(months=period_index)
        month_name = month_abbr[current_date.month - 1]
        year = current_date.year
        
        return f"{month_name} {year}"


def format_dataframe_with_period_labels(df, start_month, start_year, time_mode='monthly'):
    """
    Replace generic period column names with calendar-based labels.
    
    Args:
        df (pd.DataFrame): DataFrame with numeric column names (0, 1, 2, ...)
        start_month (int): Starting month (1-12)
        start_year (int): Starting year
        time_mode (str): 'monthly' or 'annual'
    
    Returns:
        pd.DataFrame: DataFrame with renamed columns
    
    Example:
        Input columns: [0, 1, 2, 3, ...]
        Output columns: ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', ...]
    """
    # Get numeric columns (period columns)
    numeric_cols = [col for col in df.columns if isinstance(col, (int, float))]
    
    if not numeric_cols:
        return df
    
    # Generate labels for all numeric columns
    num_periods = len(numeric_cols)
    labels = generate_period_labels(start_month, start_year, num_periods, time_mode)
    
    # Create column rename mapping
    rename_map = {col: label for col, label in zip(sorted(numeric_cols), labels)}
    
    # Rename columns
    df_renamed = df.rename(columns=rename_map)
    
    return df_renamed
