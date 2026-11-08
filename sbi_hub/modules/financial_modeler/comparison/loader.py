"""
Model loading for the Model Comparison workspace.

Two sources are supported:

- ``parse_model_file``: uploaded Financial Modeler JSON files, validated
  with the same ``validate_scenario_json`` used by the V1 "Load Model"
  flow. Uploaded files are parsed into plain ``model_inputs`` dicts —
  they are NEVER written to ``st.session_state``, so loading a
  comparison file cannot overwrite the active model.
- ``snapshot_current_model``: a deep-copied snapshot of the active
  session's model inputs (same canonical schema as a saved JSON file),
  including the session-only working-capital settings the engine uses
  but the saved-file format does not store.
"""
import copy
import json
from typing import Any, Dict, List, Optional, Tuple

from ..config.version import PLATFORM_VERSION, BUILD_DATE
from ..engine.validation import (
    session_state_to_model_inputs,
    validate_scenario_json,
)
from .schema import ModelDescriptor

# Session-state keys that the calculation engine consumes but that the
# saved-JSON format does not persist (V1 schema limitation — preserved).
SESSION_ONLY_KEYS = (
    "business_stage",
    "model_mode",
    "working_capital_source",
    "starting_ar_balance",
    "starting_ap_balance",
    "starting_inventory_balance",
)


def parse_model_file(raw: Any, filename: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Parse and validate an uploaded model file.

    Args:
        raw: File contents as ``bytes`` or ``str``.
        filename: Optional filename for error messages.

    Returns:
        ``(model_inputs, errors)`` — ``model_inputs`` is the parsed dict
        on success, ``None`` otherwise; ``errors`` is a list of
        human-readable messages (empty on success).
    """
    display_name = filename or "Uploaded file"

    if isinstance(raw, (bytes, bytearray)):
        try:
            text = bytes(raw).decode("utf-8")
        except UnicodeDecodeError:
            return None, [f"'{display_name}' is not a readable text file. "
                          "Please upload a model saved as JSON from the Financial Modeler."]
    elif isinstance(raw, str):
        text = raw
    else:
        return None, [f"'{display_name}' could not be read."]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"'{display_name}' is not valid JSON ({exc.msg} at line {exc.lineno}). "
                      "Please upload a model saved from the Financial Modeler."]

    if not isinstance(data, dict):
        return None, [f"'{display_name}' is not a Financial Modeler file "
                      "(expected a JSON object)."]

    is_valid, error_msg = validate_scenario_json(data)
    if not is_valid:
        return None, [f"'{display_name}' is not a compatible model file: {error_msg}"]

    return data, []


def snapshot_current_model(session_state) -> Dict[str, Any]:
    """
    Deep-copied snapshot of the active model's inputs.

    Uses the same ``session_state_to_model_inputs`` conversion as the
    V1 "Save Model" flow, plus the session-only working-capital keys the
    engine reads. Read-only: nothing is written back to session state.

    Args:
        session_state: Streamlit session state (or compatible object).

    Returns:
        ``model_inputs`` dict for the active model.
    """
    inputs = copy.deepcopy(session_state_to_model_inputs(session_state))

    for key in SESSION_ONLY_KEYS:
        value = session_state.get(key)
        if value is not None:
            inputs[key] = copy.deepcopy(value)

    inputs["scenario_name"] = session_state.get("scenario_name", "Current Model")
    inputs["platform_version"] = PLATFORM_VERSION
    inputs["build_date"] = BUILD_DATE

    return inputs


def describe_model(inputs: Dict[str, Any], label: str, source: str,
                   filename: Optional[str] = None) -> ModelDescriptor:
    """Build a :class:`ModelDescriptor` summary for one side of a comparison."""
    return ModelDescriptor(
        label=label,
        source=source,
        filename=filename,
        scenario_name=inputs.get("scenario_name"),
        platform_version=inputs.get("platform_version"),
        build_date=inputs.get("build_date"),
        time_mode=inputs.get("time_mode"),
        periods=inputs.get("periods"),
        revenue_stream_count=len(inputs.get("revenue_streams") or []),
        payroll_role_count=len(inputs.get("payroll_roles") or []),
        opex_item_count=len(inputs.get("opex_items") or []),
    )
