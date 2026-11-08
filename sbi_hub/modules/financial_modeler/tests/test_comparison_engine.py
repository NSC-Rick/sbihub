"""End-to-end tests for compare_models and ComparisonResult."""
import copy
import json

import pytest

from sbi_hub.modules.financial_modeler.comparison import (
    SOURCE_CURRENT_SESSION,
    compare_models,
)
from sbi_hub.modules.financial_modeler.comparison.schema import (
    STATUS_MODIFIED,
)
from sbi_hub.modules.financial_modeler.engine.validation import (
    get_default_model_inputs,
)


@pytest.fixture
def inputs():
    return get_default_model_inputs()


def test_compare_identical_models(inputs):
    result = compare_models(inputs, copy.deepcopy(inputs))

    assert result.errors == []
    assert result.counts[STATUS_MODIFIED] == 0
    assert result.annual is not None
    assert result.periodic is not None
    assert result.model_a.label == "Model A"


def test_compare_reports_descriptors(inputs):
    b = copy.deepcopy(inputs)
    b["scenario_name"] = "Variant Plan"
    result = compare_models(
        inputs, b, label_a="Original", label_b="Variant",
        filename_a="orig.json", filename_b="variant.json")

    assert result.model_a.label == "Original"
    assert result.model_a.filename == "orig.json"
    assert result.model_b.scenario_name == "Variant Plan"
    assert result.model_a.revenue_stream_count == 1


def test_version_mismatch_warning(inputs):
    a = copy.deepcopy(inputs)
    a["platform_version"] = "0.9.2"
    b = copy.deepcopy(inputs)
    b["platform_version"] = "0.9.3"

    result = compare_models(a, b)
    assert any("different platform versions" in w for w in result.warnings)


def test_missing_version_warns(inputs):
    a = copy.deepcopy(inputs)  # defaults carry no platform_version
    b = copy.deepcopy(inputs)
    b["platform_version"] = "0.9.3"

    result = compare_models(a, b)
    assert any("does not record a platform version" in w
               for w in result.warnings)


def test_engine_failure_still_returns_assumption_diff(inputs):
    broken = copy.deepcopy(inputs)
    del broken["revenue_streams"]  # validate would reject; engine errors

    result = compare_models(inputs, broken)

    # Assumption diff still produced even though outcomes failed.
    assert result.assumption_changes
    assert result.errors
    assert result.annual is None
    assert any("unavailable" in w for w in result.warnings)


def test_result_to_dict_is_json_serializable(inputs):
    b = copy.deepcopy(inputs)
    b["revenue_streams"][0]["price"] = 150.0
    b["tax_rate"] = 0.30

    result = compare_models(inputs, b)
    payload = result.to_dict()

    text = json.dumps(payload)  # must not raise
    parsed = json.loads(text)

    assert parsed["engine_version"]
    assert parsed["model_a"]["label"] == "Model A"
    assert parsed["counts"]["modified"] >= 2
    changed = {c["path"] for c in parsed["assumption_changes"]
               if c["status"] == "modified"}
    assert 'revenue_streams["Product Sales"].price' in changed
    assert "tax_rate" in changed
    assert parsed["annual"]["metrics"]["revenue"]["values_b"]


def test_current_session_source_recorded(inputs):
    result = compare_models(
        inputs, copy.deepcopy(inputs),
        source_a=SOURCE_CURRENT_SESSION, label_a="Current Model")
    assert result.model_a.source == "current_session"


def test_diff_changes_are_traceable(inputs):
    b = copy.deepcopy(inputs)
    b["revenue_streams"][0]["price"] = 150.0

    result = compare_models(inputs, b)
    change = next(
        c for c in result.assumption_changes
        if c.path == 'revenue_streams["Product Sales"].price')

    assert change.status == "modified"
    assert change.value_a == 100.0
    assert change.value_b == 150.0
    assert change.abs_diff == 50.0
    assert change.group == "Revenue Streams"
