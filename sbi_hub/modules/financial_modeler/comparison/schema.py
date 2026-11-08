"""
Structured result types for the Model Comparison workspace.

These dataclasses form the reusable contract between the comparison
engine and its consumers. The workspace UI renders them today; future
modules (Decision Insights, Experiment Sandbox, Decision Journal) are
expected to consume the same structured output via ``to_dict()``, which
produces a JSON-serializable, traceable representation of every
comparison.

Everything in this module is pure data — no Streamlit, no pandas, and no
financial calculation logic (calculations stay in the V1 engine).
"""
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

COMPARISON_ENGINE_VERSION = "2.1.0"

# Assumption change statuses
STATUS_ADDED = "added"          # present in model B only
STATUS_REMOVED = "removed"      # present in model A only
STATUS_MODIFIED = "modified"    # present in both, different value
STATUS_UNCHANGED = "unchanged"  # present in both, equal value

STATUS_LABELS = {
    STATUS_ADDED: "Added",
    STATUS_REMOVED: "Removed",
    STATUS_MODIFIED: "Modified",
    STATUS_UNCHANGED: "Unchanged",
}

# Model sources
SOURCE_CURRENT_SESSION = "current_session"
SOURCE_UPLOADED_FILE = "uploaded_file"

# Metric kinds drive display formatting
KIND_CURRENCY = "currency"
KIND_PERCENT = "percent"
KIND_RATIO = "ratio"
KIND_NUMBER = "number"


def _jsonable(value):
    """Convert a value to a JSON-serializable form."""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


@dataclass
class ModelDescriptor:
    """Identity and configuration summary for one side of a comparison."""
    label: str
    source: str
    filename: Optional[str] = None
    scenario_name: Optional[str] = None
    platform_version: Optional[str] = None
    build_date: Optional[str] = None
    time_mode: Optional[str] = None
    periods: Optional[int] = None
    revenue_stream_count: int = 0
    payroll_role_count: int = 0
    opex_item_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AssumptionChange:
    """
    One assumption difference between two models.

    ``path`` is a traceable locator such as
    ``revenue_streams["Product Sales"].price`` or
    ``capital_stack.uses.working_capital``. Entity-level entries (a whole
    revenue stream added/removed) carry the entity's fields in
    ``details`` instead of ``value_a``/``value_b``.
    """
    path: str
    group: str
    label: str
    status: str
    value_a: Any = None
    value_b: Any = None
    abs_diff: Optional[float] = None
    pct_diff: Optional[float] = None
    entity: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "group": self.group,
            "label": self.label,
            "status": self.status,
            "value_a": _jsonable(self.value_a),
            "value_b": _jsonable(self.value_b),
            "abs_diff": _jsonable(self.abs_diff),
            "pct_diff": _jsonable(self.pct_diff),
            "entity": self.entity,
            "details": _jsonable(self.details),
        }


@dataclass
class MetricComparison:
    """Aligned per-period comparison for a single financial outcome."""
    key: str
    label: str
    kind: str          # KIND_CURRENCY | KIND_PERCENT | KIND_RATIO
    agg: str           # 'sum' | 'last' | 'ratio' — how periods aggregate
    period_labels: List[str]
    values_a: List[Optional[float]]
    values_b: List[Optional[float]]
    diff: List[Optional[float]]
    pct_diff: List[Optional[float]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OutcomeView:
    """A full set of aligned financial outcome comparisons on one basis."""
    basis: str                                # 'monthly' | 'annual'
    period_labels: List[str]
    metrics: Dict[str, MetricComparison]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "basis": self.basis,
            "period_labels": list(self.period_labels),
            "metrics": {k: m.to_dict() for k, m in self.metrics.items()},
            "notes": list(self.notes),
        }


@dataclass
class ComparisonResult:
    """
    Complete, traceable result of comparing two models.

    Consumed today by the comparison workspace UI; designed to be the
    input contract for future Decision Insights, Experiment Sandbox, and
    Decision Journal modules.
    """
    engine_version: str
    generated_at: str
    model_a: ModelDescriptor
    model_b: ModelDescriptor
    assumption_changes: List[AssumptionChange]
    counts: Dict[str, int]
    warnings: List[str] = field(default_factory=list)
    rules_applied: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    annual: Optional[OutcomeView] = None
    periodic: Optional[OutcomeView] = None

    def changes_by_status(self, status: str) -> List[AssumptionChange]:
        return [c for c in self.assumption_changes if c.status == status]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_version": self.engine_version,
            "generated_at": self.generated_at,
            "model_a": self.model_a.to_dict(),
            "model_b": self.model_b.to_dict(),
            "counts": dict(self.counts),
            "warnings": list(self.warnings),
            "rules_applied": list(self.rules_applied),
            "errors": list(self.errors),
            "assumption_changes": [c.to_dict() for c in self.assumption_changes],
            "annual": self.annual.to_dict() if self.annual else None,
            "periodic": self.periodic.to_dict() if self.periodic else None,
        }
