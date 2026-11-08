"""Financial Modeler V1 calculation parity test.

Rebuilds a fixed synthetic scenario through ``build_model`` and compares
the serialized outputs against the recorded V1 baseline
(``tests/baselines/fm_v1_baseline.json``). Any change to FM calculation
behavior — intentional or accidental — fails this test and must be
explicitly re-baselined (see VERSIONING.md).
"""
import hashlib
import json
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from sbi_hub.modules.financial_modeler.engine.model import build_model  # noqa: E402

BASELINE_PATH = Path(__file__).resolve().parent / "baselines" / "fm_v1_baseline.json"


def _to_jsonable(obj):
    if isinstance(obj, pd.DataFrame):
        return {"__dataframe__": _to_jsonable(obj.to_dict(orient="list"))}
    if isinstance(obj, pd.Series):
        return {"__series__": _to_jsonable(obj.tolist())}
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return round(float(obj), 6)
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj


@pytest.fixture(scope="module")
def baseline():
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def current_outputs(baseline):
    return _to_jsonable(build_model(baseline["inputs"]))


def _digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def test_output_structure_keys_match(baseline, current_outputs):
    assert set(current_outputs) == set(baseline["outputs"]), (
        f"build_model output keys changed: "
        f"{set(current_outputs) ^ set(baseline['outputs'])}"
    )


def test_calculation_outputs_match_v1_baseline(baseline, current_outputs):
    digest = _digest(current_outputs)
    assert digest == baseline["outputs_sha256"], (
        f"FM outputs diverged from V1 baseline "
        f"(expected {baseline['outputs_sha256']}, got {digest}). "
        f"Differing keys: "
        f"{[k for k in current_outputs if current_outputs[k] != baseline['outputs'][k]]}"
    )
