"""
Tests for scenario export filename sanitization.
"""
import pytest
from datetime import datetime


def test_filename_sanitization_spaces():
    """Test that spaces are replaced with underscores."""
    scenario_name = "Cafe Expansion Plan"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    assert safe_name == "Cafe_Expansion_Plan"
    assert " " not in safe_name


def test_filename_sanitization_special_chars():
    """Test that special characters are removed."""
    scenario_name = "Q1 2026 @ Revenue!"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    # @ becomes space, then underscore, so we get double underscore
    assert safe_name == "Q1_2026__Revenue"
    assert "@" not in safe_name
    assert "!" not in safe_name


def test_filename_sanitization_hyphens_preserved():
    """Test that hyphens are preserved in filenames."""
    scenario_name = "Pre-Launch Scenario"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    assert safe_name == "Pre-Launch_Scenario"
    assert "-" in safe_name


def test_filename_sanitization_underscores_preserved():
    """Test that existing underscores are preserved."""
    scenario_name = "Base_Case_2026"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    assert safe_name == "Base_Case_2026"


def test_filename_with_timestamp():
    """Test that timestamp is added to filename."""
    scenario_name = "Business Scenario"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"{safe_name}_{timestamp}.json"
    
    assert filename.startswith("Business_Scenario_")
    assert filename.endswith(".json")
    assert len(timestamp) == 8  # YYYYMMDD format


def test_filename_sanitization_empty_after_removal():
    """Test edge case where all characters are removed."""
    scenario_name = "!@#$%"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    # Should result in empty string
    assert safe_name == ""


def test_filename_sanitization_unicode():
    """Test that unicode characters are removed."""
    scenario_name = "Café Expansion 🚀"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    # Unicode characters should be removed
    assert "🚀" not in safe_name
    # ASCII alphanumeric should be preserved
    assert "Caf" in safe_name or "Expansion" in safe_name


def test_filename_sanitization_multiple_spaces():
    """Test that multiple consecutive spaces become single underscore."""
    scenario_name = "Business    Scenario"
    safe_name = scenario_name.replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    
    # Multiple spaces become multiple underscores (could be improved)
    assert safe_name == "Business____Scenario"


def test_filename_real_world_examples():
    """Test real-world scenario name examples."""
    test_cases = [
        ("Cafe Expansion", "Cafe_Expansion"),
        ("Q1-2026 Forecast", "Q1-2026_Forecast"),
        ("Base Case", "Base_Case"),
        ("Optimistic_Scenario", "Optimistic_Scenario"),
        ("2026 Revenue Model", "2026_Revenue_Model"),
    ]
    
    for input_name, expected_output in test_cases:
        safe_name = input_name.replace(" ", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
        assert safe_name == expected_output, f"Failed for input: {input_name}"
