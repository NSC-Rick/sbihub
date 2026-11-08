"""
Comparison engine orchestrator.

``compare_models`` is the single entry point used by both comparison
modes (Saved vs Saved, Current vs Saved). It produces a
:class:`ComparisonResult` containing the assumption diff, aligned
financial outcome comparisons, warnings, and the documented rules that
were applied — all traceable and JSON-serializable via ``to_dict()``.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .diff import count_by_status, diff_model_inputs
from .loader import describe_model
from .outcomes import compare_outcomes, evaluate_model
from .schema import (
    COMPARISON_ENGINE_VERSION,
    ComparisonResult,
    SOURCE_UPLOADED_FILE,
)


def compare_models(inputs_a: Dict[str, Any], inputs_b: Dict[str, Any],
                   label_a: str = "Model A", label_b: str = "Model B",
                   source_a: str = SOURCE_UPLOADED_FILE,
                   source_b: str = SOURCE_UPLOADED_FILE,
                   filename_a: Optional[str] = None,
                   filename_b: Optional[str] = None) -> ComparisonResult:
    """
    Compare two Financial Modeler models end to end.

    Args:
        inputs_a: Original model_inputs dict.
        inputs_b: Comparison model_inputs dict.
        label_a / label_b: Display labels for each side.
        source_a / source_b: ``SOURCE_CURRENT_SESSION`` or
            ``SOURCE_UPLOADED_FILE`` (descriptor only — both sides are
            already plain dicts).
        filename_a / filename_b: Uploaded filenames, when applicable.

    Returns:
        A fully populated :class:`ComparisonResult`. Engine failures for
        either model are captured in ``errors`` (the assumption diff
        still runs — it needs no calculation).
    """
    descriptor_a = describe_model(inputs_a, label_a, source_a, filename_a)
    descriptor_b = describe_model(inputs_b, label_b, source_b, filename_b)

    warnings = []
    version_a = inputs_a.get("platform_version")
    version_b = inputs_b.get("platform_version")
    if version_a and version_b and version_a != version_b:
        warnings.append(
            f"The models were saved by different platform versions "
            f"({version_a} vs {version_b}). Results may use different "
            "calculation defaults — differences are flagged where known."
        )
    elif version_a != version_b:
        warnings.append(
            "One model does not record a platform version. It may have "
            "been created by an older release or by hand — defaults are "
            "applied for any missing settings."
        )

    assumption_changes = diff_model_inputs(inputs_a, inputs_b)
    counts = count_by_status(assumption_changes)

    errors = []
    outputs_a, error_a = evaluate_model(inputs_a)
    outputs_b, error_b = evaluate_model(inputs_b)
    if error_a:
        errors.append(f"{label_a}: {error_a}")
    if error_b:
        errors.append(f"{label_b}: {error_b}")

    periodic = annual = None
    rules = []
    if outputs_a is not None and outputs_b is not None:
        periodic, annual, outcome_warnings, rules = compare_outcomes(
            outputs_a, inputs_a, outputs_b, inputs_b
        )
        warnings.extend(outcome_warnings)
    else:
        warnings.append(
            "Financial outcomes are unavailable for the model(s) listed "
            "above; only assumption differences are shown."
        )

    return ComparisonResult(
        engine_version=COMPARISON_ENGINE_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        model_a=descriptor_a,
        model_b=descriptor_b,
        assumption_changes=assumption_changes,
        counts=counts,
        warnings=warnings,
        rules_applied=rules,
        errors=errors,
        annual=annual,
        periodic=periodic,
    )
