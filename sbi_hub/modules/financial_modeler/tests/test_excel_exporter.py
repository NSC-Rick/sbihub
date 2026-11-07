"""
Test Excel Exporter Sanitization (WPP-EXPORT-EXCEL-001)

Validates that the Excel exporter correctly sanitizes column names,
sheet names, and handles JSON payloads without errors.
"""

import pytest
import pandas as pd
from io import BytesIO
from sbi_hub.modules.financial_modeler.utils.exporters import (
    sanitize_excel_column_name,
    sanitize_dataframe_for_excel,
    sanitize_sheet_name,
    safe_to_excel,
    export_scenario_to_excel,
    OPENPYXL_AVAILABLE
)

# Skip all tests if openpyxl is not available
pytestmark = pytest.mark.skipif(not OPENPYXL_AVAILABLE, reason="openpyxl not installed")


def test_sanitize_excel_column_name_brackets():
    """
    TEST 2: Bracket columns should be converted to parentheses.
    
    Input: Revenue[Monthly]
    Expected: Revenue(Monthly)
    """
    assert sanitize_excel_column_name("Revenue[Monthly]") == "Revenue(Monthly)"
    assert sanitize_excel_column_name("COGS[Food]") == "COGS(Food)"
    assert sanitize_excel_column_name("Payroll[Staff]") == "Payroll(Staff)"
    
    print("✅ TEST 2 PASSED: Bracket columns converted to parentheses")


def test_sanitize_excel_column_name_special_chars():
    """
    Test that special characters are removed from column names.
    
    Excel column names cannot contain: \ / * ? : [ ]
    """
    assert sanitize_excel_column_name("Column:Name") == "ColumnName"
    assert sanitize_excel_column_name("Column*Name") == "ColumnName"
    assert sanitize_excel_column_name("Column?Name") == "ColumnName"
    assert sanitize_excel_column_name("Column/Name") == "ColumnName"
    assert sanitize_excel_column_name("Column\\Name") == "ColumnName"
    
    print("✅ TEST PASSED: Special characters removed from column names")


def test_sanitize_dataframe_for_excel():
    """
    Test that dataframe columns are sanitized correctly.
    """
    df = pd.DataFrame({
        "Revenue[Monthly]": [100, 200, 300],
        "COGS[Food]": [30, 60, 90],
        "Payroll[Staff]": [50, 50, 50]
    })
    
    sanitized_df = sanitize_dataframe_for_excel(df)
    
    assert "Revenue(Monthly)" in sanitized_df.columns
    assert "COGS(Food)" in sanitized_df.columns
    assert "Payroll(Staff)" in sanitized_df.columns
    
    # Original should not be modified
    assert "Revenue[Monthly]" in df.columns
    
    print("✅ TEST PASSED: DataFrame columns sanitized correctly")


def test_sanitize_sheet_name_special_chars():
    """
    Test that sheet names with special characters are sanitized.
    """
    assert sanitize_sheet_name("Sheet[1]") == "Sheet1"
    assert sanitize_sheet_name("Sheet:Name") == "SheetName"
    assert sanitize_sheet_name("Sheet*Name") == "SheetName"
    assert sanitize_sheet_name("Sheet?Name") == "SheetName"
    assert sanitize_sheet_name("Sheet/Name") == "SheetName"
    assert sanitize_sheet_name("Sheet\\Name") == "SheetName"
    
    print("✅ TEST PASSED: Sheet name special characters removed")


def test_sanitize_sheet_name_long():
    """
    TEST 4: Long sheet names should be truncated to 31 characters.
    """
    long_name = "This_Is_A_Very_Long_Sheet_Name_That_Exceeds_31_Characters"
    sanitized = sanitize_sheet_name(long_name)
    
    assert len(sanitized) <= 31
    assert sanitized == long_name[:31]
    
    print(f"✅ TEST 4 PASSED: Long sheet name truncated")
    print(f"   Original length: {len(long_name)}")
    print(f"   Sanitized length: {len(sanitized)}")


def test_sanitize_sheet_name_empty():
    """
    Test that empty sheet names are handled.
    """
    assert sanitize_sheet_name("") == "Sheet"
    assert sanitize_sheet_name("   ") == "Sheet"
    
    print("✅ TEST PASSED: Empty sheet names handled")


def test_safe_to_excel_with_dict():
    """
    TEST 3: JSON payload (dict) should be converted to DataFrame.
    """
    if not OPENPYXL_AVAILABLE:
        pytest.skip("openpyxl not installed")
    
    buffer = BytesIO()
    
    # Create a dict (JSON payload)
    json_data = {
        "key1": "value1",
        "key2": "value2",
        "key3": 123
    }
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        safe_to_excel(json_data, writer, "JSON_Sheet", index=False)
    
    # Read back to verify
    buffer.seek(0)
    df_read = pd.read_excel(buffer, sheet_name="JSON_Sheet")
    
    assert "key1" in df_read.columns
    assert "key2" in df_read.columns
    assert "key3" in df_read.columns
    
    print("✅ TEST 3 PASSED: JSON payload converted to DataFrame")


def test_safe_to_excel_with_bracket_columns():
    """
    Test that safe_to_excel sanitizes bracket columns.
    """
    if not OPENPYXL_AVAILABLE:
        pytest.skip("openpyxl not installed")
    
    buffer = BytesIO()
    
    df = pd.DataFrame({
        "Revenue[Monthly]": [100, 200, 300],
        "COGS[Food]": [30, 60, 90]
    })
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        safe_to_excel(df, writer, "Test_Sheet", index=False)
    
    # Read back to verify
    buffer.seek(0)
    df_read = pd.read_excel(buffer, sheet_name="Test_Sheet")
    
    assert "Revenue(Monthly)" in df_read.columns
    assert "COGS(Food)" in df_read.columns
    
    print("✅ TEST PASSED: Bracket columns sanitized in Excel export")


def test_export_scenario_to_excel_standard():
    """
    TEST 1: Standard export with normal column names.
    
    Expected: Excel file downloads successfully
    """
    if not OPENPYXL_AVAILABLE:
        pytest.skip("openpyxl not installed")
    
    # Create minimal model inputs
    model_inputs = {
        'scenario_name': 'Test Scenario',
        'time_mode': 'monthly',
        'periods': 12,
        'global_cogs_pct': 0.3,
        'revenue_streams': [],
        'payroll_roles': [],
        'loan_principal': 100000,
        'loan_annual_rate': 0.07,
        'loan_term_months': 60
    }
    
    # Create sample DataFrames
    income_statement = pd.DataFrame({
        0: [100000, 30000, 70000, 20000, 50000],
        1: [110000, 33000, 77000, 22000, 55000]
    }, index=['Revenue', 'COGS', 'Gross Profit', 'Expenses', 'Net Income'])
    
    cash_flow = pd.DataFrame({
        0: [50000, -10000, 5000, 45000],
        1: [55000, -11000, 5500, 49500]
    }, index=['Net Income', 'Working Capital Change', 'Financing', 'Ending Cash'])
    
    # Export to Excel
    excel_bytes = export_scenario_to_excel(
        model_inputs=model_inputs,
        income_statement_df=income_statement,
        cash_flow_df=cash_flow,
        include_raw_json=True
    )
    
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0
    
    # Verify we can read it back
    buffer = BytesIO(excel_bytes)
    excel_file = pd.ExcelFile(buffer)
    
    assert 'Scenario' in excel_file.sheet_names
    assert 'Summary' in excel_file.sheet_names
    
    print("✅ TEST 1 PASSED: Standard export successful")
    print(f"   Excel file size: {len(excel_bytes)} bytes")
    print(f"   Sheets: {excel_file.sheet_names}")


def test_export_scenario_with_bracket_columns():
    """
    Test export with bracket columns in DataFrames.
    
    The key test is that export does NOT raise ValueError.
    Index names are preserved as-is in Excel (they're row labels, not column names).
    """
    if not OPENPYXL_AVAILABLE:
        pytest.skip("openpyxl not installed")
    
    model_inputs = {
        'scenario_name': 'Bracket Test',
        'time_mode': 'monthly',
        'periods': 3
    }
    
    # Create DataFrame with bracket columns (column headers)
    income_statement = pd.DataFrame({
        'Revenue[Monthly]': [100000, 110000],
        'COGS[Food]': [30000, 33000]
    })
    
    # Export should not raise ValueError
    try:
        excel_bytes = export_scenario_to_excel(
            model_inputs=model_inputs,
            income_statement_df=income_statement,
            include_raw_json=False
        )
        
        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0
        
        # Verify columns were sanitized when reading back
        buffer = BytesIO(excel_bytes)
        df_read = pd.read_excel(buffer, sheet_name='Income_Statement')
        
        # Columns should be sanitized (brackets converted to parentheses)
        assert 'Revenue(Monthly)' in df_read.columns
        assert 'COGS(Food)' in df_read.columns
        
        print("✅ TEST PASSED: Export with bracket columns successful")
        print(f"   Sanitized columns: {list(df_read.columns)}")
        
    except ValueError as e:
        if "is not a valid column name" in str(e):
            pytest.fail(f"ValueError on bracket columns: {e}")
        else:
            raise


def test_export_scenario_with_long_sheet_names():
    """
    Test that long sheet names are handled correctly.
    """
    if not OPENPYXL_AVAILABLE:
        pytest.skip("openpyxl not installed")
    
    model_inputs = {
        'scenario_name': 'Test_Scenario_With_Very_Long_Name_That_Exceeds_31_Characters',
        'time_mode': 'monthly',
        'periods': 3
    }
    
    # Export should not raise error
    excel_bytes = export_scenario_to_excel(
        model_inputs=model_inputs,
        include_raw_json=False
    )
    
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0
    
    print("✅ TEST PASSED: Export with long sheet names successful")


def test_no_value_error_on_bracket_columns():
    """
    Regression test: Ensure '[' does not cause ValueError.
    
    This was the original bug that triggered WPP-EXPORT-EXCEL-001.
    """
    if not OPENPYXL_AVAILABLE:
        pytest.skip("openpyxl not installed")
    
    buffer = BytesIO()
    
    # Create DataFrame with problematic column name
    df = pd.DataFrame({
        "[Problematic]": [1, 2, 3],
        "Normal": [4, 5, 6]
    })
    
    # This should NOT raise ValueError: '[' is not a valid column name
    try:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            safe_to_excel(df, writer, "Test", index=False)
        
        print("✅ REGRESSION TEST PASSED: No ValueError on bracket columns")
    except ValueError as e:
        if "is not a valid column name" in str(e):
            pytest.fail(f"ValueError still occurs: {e}")
        else:
            raise


if __name__ == '__main__':
    # Run all tests
    if OPENPYXL_AVAILABLE:
        test_sanitize_excel_column_name_brackets()
        test_sanitize_excel_column_name_special_chars()
        test_sanitize_dataframe_for_excel()
        test_sanitize_sheet_name_special_chars()
        test_sanitize_sheet_name_long()
        test_sanitize_sheet_name_empty()
        test_safe_to_excel_with_dict()
        test_safe_to_excel_with_bracket_columns()
        test_export_scenario_to_excel_standard()
        test_export_scenario_with_bracket_columns()
        test_export_scenario_with_long_sheet_names()
        test_no_value_error_on_bracket_columns()
        
        print("\n" + "="*70)
        print("✅ ALL EXCEL EXPORTER TESTS PASSED")
        print("="*70)
    else:
        print("⚠️ openpyxl not installed - tests skipped")
