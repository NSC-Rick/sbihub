"""
Model Comparison workspace — SBI Financial Modeler V2.1.

A modular workspace for comparing two Financial Modeler models:
assumption differences and financial outcome differences, evaluated
independently with the unchanged V1 calculation engine.

Public API (consumed by the workspace UI today; designed as the input
contract for future Decision Insights, Experiment Sandbox, and Decision
Journal modules):

- ``compare_models(inputs_a, inputs_b, ...)`` → ``ComparisonResult``
- ``parse_model_file(raw, filename)`` → ``(model_inputs, errors)``
- ``snapshot_current_model(session_state)`` → ``model_inputs``
- ``ComparisonResult.to_dict()`` → JSON-serializable result
"""
from .engine import compare_models
from .loader import describe_model, parse_model_file, snapshot_current_model
from .schema import (
    COMPARISON_ENGINE_VERSION,
    SOURCE_CURRENT_SESSION,
    SOURCE_UPLOADED_FILE,
    STATUS_ADDED,
    STATUS_MODIFIED,
    STATUS_REMOVED,
    STATUS_UNCHANGED,
    AssumptionChange,
    ComparisonResult,
    MetricComparison,
    ModelDescriptor,
    OutcomeView,
)

__all__ = [
    "compare_models",
    "describe_model",
    "parse_model_file",
    "snapshot_current_model",
    "COMPARISON_ENGINE_VERSION",
    "SOURCE_CURRENT_SESSION",
    "SOURCE_UPLOADED_FILE",
    "STATUS_ADDED",
    "STATUS_MODIFIED",
    "STATUS_REMOVED",
    "STATUS_UNCHANGED",
    "AssumptionChange",
    "ComparisonResult",
    "MetricComparison",
    "ModelDescriptor",
    "OutcomeView",
]
