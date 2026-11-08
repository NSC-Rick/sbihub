"""
Assumption diff engine for the Model Comparison workspace.

Compares two ``model_inputs`` dicts (the same canonical schema used by
saved scenario JSON files) and produces a flat, traceable list of
:class:`AssumptionChange` entries.

Rules (documented for consumers):

- Scalars are compared with a small numeric tolerance
  (``math.isclose``, rel/abs 1e-9). Equal values are ``unchanged``;
  different values are ``modified`` with ``abs_diff`` (B - A) and
  ``pct_diff`` ((B - A) / A, stored as a decimal fraction; ``None`` when
  A is zero or either side is non-numeric).
- Keys present in only one model produce ``added``/``removed`` leaves.
- Lists of dicts with a shared identity key (``name`` or ``role``) are
  matched as entities by that key — e.g. a revenue stream named
  "Product Sales" in both models is compared field-by-field. Entities
  only in A are ``removed``; only in B are ``added`` (entity-level entry
  carrying its fields in ``details``).
- Lists of scalars (e.g. seasonality ``custom_weights``) are compared
  element-wise by index.
- Nested dicts (``capital_stack``, ``owner_compensation``,
  ``seasonality``) are diffed recursively; a missing parent expands to
  per-leaf added/removed entries.
"""
import math
from typing import Any, Dict, List, Optional, Tuple

from .schema import (
    AssumptionChange,
    STATUS_ADDED,
    STATUS_MODIFIED,
    STATUS_REMOVED,
    STATUS_UNCHANGED,
)

_MISSING = object()

_MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Ordered (top-level key -> group) rules; first match wins.
_GROUP_RULES: List[Tuple[str, str]] = [
    ("scenario_name", "Model Info"),
    ("platform_version", "Model Info"),
    ("build_date", "Model Info"),
    ("time_mode", "Forecast & Configuration"),
    ("periods", "Forecast & Configuration"),
    ("mode", "Forecast & Configuration"),
    ("revenue_streams", "Revenue Streams"),
    ("revenue_input_method", "Revenue Inputs"),
    ("monthly_revenue", "Revenue Inputs"),
    ("avg_sale", "Revenue Inputs"),
    ("monthly_transactions", "Revenue Inputs"),
    ("customers_per_day", "Revenue Inputs"),
    ("days_open", "Revenue Inputs"),
    ("global_cogs_pct", "Cost of Goods"),
    ("cogs_improvement_pct", "Cost of Goods"),
    ("payroll_roles", "Payroll & Staffing"),
    ("opex_items", "Operating Expenses"),
    ("loan_principal", "Financing"),
    ("loan_annual_rate", "Financing"),
    ("loan_term_months", "Financing"),
    ("loan_start_period", "Financing"),
    ("business_loan_amount", "Financing"),
    ("business_interest_rate", "Financing"),
    ("business_amort_years", "Financing"),
    ("real_estate_loan_amount", "Financing"),
    ("real_estate_interest_rate", "Financing"),
    ("real_estate_amort_years", "Financing"),
    ("capital_stack", "Capital Structure"),
    ("ar_days", "Working Capital"),
    ("ap_days", "Working Capital"),
    ("inventory_days", "Working Capital"),
    ("business_stage", "Business Stage & Session Settings"),
    ("model_mode", "Business Stage & Session Settings"),
    ("working_capital_source", "Business Stage & Session Settings"),
    ("starting_ar_balance", "Business Stage & Session Settings"),
    ("starting_ap_balance", "Business Stage & Session Settings"),
    ("starting_inventory_balance", "Business Stage & Session Settings"),
    ("tax_rate", "Taxes & Depreciation"),
    ("annual_depreciation", "Taxes & Depreciation"),
    ("owner_compensation", "Owner Compensation"),
    ("seasonality", "Seasonality & Ramp"),
    ("startup_ramp_months", "Seasonality & Ramp"),
]

_FIELD_LABELS: Dict[str, str] = {
    "scenario_name": "Model name",
    "platform_version": "Platform version",
    "build_date": "Build date",
    "time_mode": "Time mode",
    "periods": "Forecast length (periods)",
    "mode": "Input mode",
    "name": "Name",
    "price": "Price per unit",
    "volume": "Starting volume per period",
    "growth_rate": "Annual growth rate",
    "cogs_override": "COGS override",
    "global_cogs_pct": "Global COGS",
    "cogs_improvement_pct": "Annual COGS improvement",
    "role": "Role",
    "headcount": "Headcount",
    "pay_type": "Pay type",
    "rate": "Pay rate",
    "hours_per_week": "Hours per week",
    "annual_raise_pct": "Annual raise",
    "payroll_tax_pct": "Payroll tax rate",
    "benefits_pct": "Benefits rate",
    "role_type": "Role type",
    "amount": "Amount",
    "category": "Expense category",
    "loan_principal": "Loan principal",
    "loan_annual_rate": "Loan annual interest rate",
    "loan_term_months": "Loan term (months)",
    "loan_start_period": "Loan start period",
    "business_loan_amount": "Business loan amount",
    "business_interest_rate": "Business loan interest rate",
    "business_amort_years": "Business loan amortization (years)",
    "real_estate_loan_amount": "Real estate loan amount",
    "real_estate_interest_rate": "Real estate loan interest rate",
    "real_estate_amort_years": "Real estate amortization (years)",
    "enabled": "Enabled",
    "purchase_price": "Purchase price (legacy)",
    "closing_costs": "Closing costs (legacy)",
    "business_purchase_price": "Business purchase price",
    "inventory_adjustment": "Inventory adjustment",
    "business_closing_costs": "Business closing costs",
    "real_estate_purchase": "Real estate purchase",
    "real_estate_closing_costs": "Real estate closing costs",
    "working_capital": "Working capital funding",
    "capex": "Capital expenditures",
    "buyer_equity": "Buyer equity",
    "community_equity": "Community equity",
    "donations": "Donations",
    "bank_loan": "Bank loan",
    "seller_note": "Seller note",
    "term": "Term (years)",
    "ar_days": "Accounts receivable days",
    "ap_days": "Accounts payable days",
    "inventory_days": "Inventory days",
    "business_stage": "Business stage",
    "model_mode": "Model mode",
    "working_capital_source": "Working capital source",
    "starting_ar_balance": "Starting AR balance",
    "starting_ap_balance": "Starting AP balance",
    "starting_inventory_balance": "Starting inventory balance",
    "tax_rate": "Tax rate",
    "annual_depreciation": "Annual depreciation",
    "custom_weights": "Custom monthly weights",
    "revenue_input_method": "Revenue input method",
    "monthly_revenue": "Monthly revenue target",
    "avg_sale": "Average sale",
    "monthly_transactions": "Monthly transactions",
    "customers_per_day": "Customers per day",
    "days_open": "Days open per month",
    "startup_ramp_months": "Startup ramp (months)",
    "monthly_revenue_target": "Monthly revenue target",
}

_ENTITY_LABELS = {
    "revenue_streams": "Revenue stream",
    "payroll_roles": "Payroll role",
    "opex_items": "Operating expense",
}

# Leaf keys whose values are decimal fractions shown as percentages.
_PERCENT_KEYS = {
    "growth_rate", "annual_raise_pct", "payroll_tax_pct", "benefits_pct",
    "global_cogs_pct", "cogs_improvement_pct", "cogs_override", "tax_rate",
    "loan_annual_rate", "business_interest_rate", "real_estate_interest_rate",
}

# Leaf keys shown as currency. 'amount'/'rate' are context-sensitive and
# resolved in ``_format_hint``.
_CURRENCY_KEYS = {
    "price", "loan_principal", "business_loan_amount",
    "real_estate_loan_amount", "annual_depreciation", "monthly_revenue",
    "avg_sale", "purchase_price", "closing_costs",
    "business_purchase_price", "inventory_adjustment",
    "business_closing_costs", "real_estate_purchase",
    "real_estate_closing_costs", "working_capital", "capex",
    "buyer_equity", "community_equity", "donations",
    "starting_ar_balance", "starting_ap_balance",
    "starting_inventory_balance",
}

# Leaf keys shown as whole numbers.
_INTEGER_KEYS = {
    "headcount", "hours_per_week", "periods", "loan_term_months",
    "loan_start_period", "ar_days", "ap_days", "inventory_days", "term",
    "business_amort_years", "real_estate_amort_years",
    "startup_ramp_months",
}


def _top_key(path: List[str]) -> str:
    return path[0] if path else ""


def _group_for(path: List[str]) -> str:
    top = _top_key(path)
    for key, group in _GROUP_RULES:
        if top == key:
            return group
    return "Other Assumptions"


def _leaf_key(path: List[str]) -> str:
    return path[-1] if path else ""


def _field_label(path: List[str]) -> str:
    key = _leaf_key(path)
    if key == "rate":
        # Payroll 'rate' is a wage; capital-stack 'rate' is interest.
        return "Pay rate" if _top_key(path) == "payroll_roles" else "Interest rate"
    label = _FIELD_LABELS.get(key)
    if label:
        return label
    return key.replace("_", " ").strip().capitalize() if key else "Value"


def _identity_key(items: List[Any]) -> Optional[str]:
    """Return the shared identity key for a list of entity dicts, else None."""
    if not items or not all(isinstance(i, dict) for i in items):
        return None
    for candidate in ("name", "role"):
        if all(candidate in i for i in items):
            return candidate
    return None


def _values_equal(a: Any, b: Any) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
            and not isinstance(a, bool) and not isinstance(b, bool):
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)
    return a == b


def _diff_dict(a: Dict[str, Any], b: Dict[str, Any], path: List[str],
               out: List[AssumptionChange]) -> None:
    for key in sorted(set(a) | set(b)):
        _diff_value(a.get(key, _MISSING), b.get(key, _MISSING),
                    path + [str(key)], out)


def _diff_list(a: List[Any], b: List[Any], path: List[str],
               out: List[AssumptionChange]) -> None:
    key_a = _identity_key(a)
    key_b = _identity_key(b)
    top = _top_key(path)
    entity_label = _ENTITY_LABELS.get(top, top.replace("_", " ").rstrip("s"))

    # Entity semantics apply when both sides match on one identity key,
    # or when one side is empty and the other has identity-keyed items.
    if key_a and key_a == key_b:
        _diff_entity_list(a, b, key_a, path, out)
    elif key_a and not b:
        for item in a:
            out.append(_entity_change(item, STATUS_REMOVED, path, entity_label))
    elif key_b and not a:
        for item in b:
            out.append(_entity_change(item, STATUS_ADDED, path, entity_label))
    else:
        _diff_indexed_list(a, b, path, out)


def _diff_entity_list(a: List[Dict[str, Any]], b: List[Dict[str, Any]],
                      id_key: str, path: List[str],
                      out: List[AssumptionChange]) -> None:
    top = _top_key(path)
    entity_label = _ENTITY_LABELS.get(top, top.replace("_", " ").rstrip("s"))

    matched_b = set()
    for item_a in a:
        name_a = item_a.get(id_key)
        match_idx = next(
            (i for i, item_b in enumerate(b)
             if i not in matched_b and item_b.get(id_key) == name_a),
            None,
        )
        if match_idx is None:
            out.append(_entity_change(item_a, STATUS_REMOVED, path, entity_label))
        else:
            matched_b.add(match_idx)
            entity_path = path + [f'"{name_a}"']
            _diff_dict(item_a, b[match_idx], entity_path, out)

    for i, item_b in enumerate(b):
        if i not in matched_b:
            out.append(_entity_change(item_b, STATUS_ADDED, path, entity_label))


def _entity_change(item: Dict[str, Any], status: str, path: List[str],
                   entity_label: str) -> AssumptionChange:
    name = item.get("name", item.get("role", "Unnamed"))
    value = dict(item) if status == STATUS_ADDED else None
    return AssumptionChange(
        path=f'{_path_str(path)}["{name}"]',
        group=_group_for(path),
        label=f'{entity_label.capitalize()} "{name}"',
        status=status,
        value_a=None if status == STATUS_ADDED else dict(item),
        value_b=value,
        entity=str(name),
        details=dict(item),
    )


def _diff_indexed_list(a: List[Any], b: List[Any], path: List[str],
                       out: List[AssumptionChange]) -> None:
    for i in range(max(len(a), len(b))):
        va = a[i] if i < len(a) else _MISSING
        vb = b[i] if i < len(b) else _MISSING
        _diff_value(va, vb, path + [f"[{i}]"], out)


def _diff_value(va: Any, vb: Any, path: List[str],
                out: List[AssumptionChange]) -> None:
    if va is _MISSING and vb is _MISSING:
        return

    # Recurse into dicts present on both sides.
    if isinstance(va, dict) and isinstance(vb, dict):
        _diff_dict(va, vb, path, out)
        return

    # Lists present on both sides.
    if isinstance(va, list) and isinstance(vb, list):
        _diff_list(va, vb, path, out)
        return

    # Missing on one side: expand containers leaf-by-leaf.
    if va is _MISSING:
        if isinstance(vb, dict):
            _diff_dict({}, vb, path, out)
        elif isinstance(vb, list):
            _diff_indexed_list([], vb, path, out)
        else:
            out.append(_leaf_change(_MISSING, vb, path, STATUS_ADDED))
        return
    if vb is _MISSING:
        if isinstance(va, dict):
            _diff_dict(va, {}, path, out)
        elif isinstance(va, list):
            _diff_indexed_list(va, [], path, out)
        else:
            out.append(_leaf_change(va, _MISSING, path, STATUS_REMOVED))
        return

    # Both scalars (or a type change like dict -> scalar).
    status = STATUS_UNCHANGED if _values_equal(va, vb) else STATUS_MODIFIED
    out.append(_leaf_change(va, vb, path, status))


def _leaf_change(va: Any, vb: Any, path: List[str],
                 status: str) -> AssumptionChange:
    abs_diff = pct_diff = None
    if status == STATUS_MODIFIED \
            and isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
            and not isinstance(va, bool) and not isinstance(vb, bool):
        abs_diff = float(vb) - float(va)
        if va != 0:
            pct_diff = abs_diff / abs(float(va))

    label = _leaf_label(path)
    entity = _entity_name(path)
    return AssumptionChange(
        path=_path_str(path),
        group=_group_for(path),
        label=label,
        status=status,
        value_a=None if va is _MISSING else va,
        value_b=None if vb is _MISSING else vb,
        abs_diff=abs_diff,
        pct_diff=pct_diff,
        entity=entity,
    )


def _path_str(path: List[str]) -> str:
    """Human-readable path, e.g. revenue_streams["Name"].price."""
    out = ""
    for seg in path:
        if seg.startswith('"') and seg.endswith('"'):
            out += f"[{seg}]"
        elif seg.startswith("["):
            out += seg
        elif out:
            out += "." + seg
        else:
            out = seg
    return out


def _entity_name(path: List[str]) -> Optional[str]:
    for seg in path:
        if seg.startswith('"') and seg.endswith('"'):
            return seg.strip('"')
    return None


def _context_label(path: List[str]) -> Optional[str]:
    """Parent context for nested config leaves (e.g. 'Seasonality', 'Bank loan')."""
    if len(path) < 2:
        return None
    parent = path[-2]
    if parent.startswith('"') or parent.startswith("["):
        return None
    if parent in ("uses", "sources"):
        parent = path[-3] if len(path) >= 3 else parent
    if len(path) >= 3 or parent in ("owner_compensation", "seasonality", "capital_stack"):
        return _FIELD_LABELS.get(parent, parent.replace("_", " ").capitalize())
    return None


def _leaf_label(path: List[str]) -> str:
    """Plain-English label for a leaf, with entity/index/parent context."""
    entity = _entity_name(path)
    leaf = _leaf_key(path)

    if leaf.startswith("[") and leaf.endswith("]"):
        # Indexed element, e.g. seasonality.custom_weights[3]
        idx = int(leaf[1:-1])
        parent = path[-2] if len(path) >= 2 else ""
        if parent == "custom_weights" and 0 <= idx < 12:
            base = f"Custom weight — {_MONTH_NAMES[idx]}"
        else:
            base = f"{_FIELD_LABELS.get(parent, parent.replace('_', ' ').capitalize())} [{idx}]"
    else:
        base = _field_label(path)

    if entity:
        return f"{entity} · {base}"

    context = _context_label(path)
    return f"{context} — {base}" if context else base


def _format_hint(path: str, key: str) -> str:
    """Return 'percent' | 'currency' | 'integer' | 'number' display hint."""
    if key == "rate":
        # Payroll pay rate is currency; capital-stack loan rates are percent.
        return "currency" if path.startswith("payroll_roles") else "percent"
    if key in _PERCENT_KEYS:
        return "percent"
    if key == "amount":
        return "currency"
    if key in _CURRENCY_KEYS:
        return "currency"
    if key in _INTEGER_KEYS:
        return "integer"
    return "number"


def format_assumption_value(value: Any, path: str = "", key: str = "") -> str:
    """
    Format an assumption value for display.

    Args:
        value: The raw value.
        path: Full change path (used for context-sensitive hints like
            payroll ``rate`` vs capital-stack ``rate``).
        key: The leaf key (defaults to last path segment).
    """
    if not key and path:
        tail = path.replace("]", "").rsplit(".", 1)[-1]
        key = tail.rsplit("[", 1)[-1] if "[" in tail else tail
    hint = _format_hint(path, key)

    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        if hint == "percent":
            return f"{value * 100:,.2f}%"
        if hint == "currency":
            return f"${value:,.2f}"
        if hint == "integer":
            return f"{value:,.0f}"
        return f"{value:,.2f}"
    if isinstance(value, dict):
        return f"{len(value)} fields"
    if isinstance(value, list):
        return f"{len(value)} items"
    return str(value)


def diff_model_inputs(inputs_a: Dict[str, Any],
                      inputs_b: Dict[str, Any]) -> List[AssumptionChange]:
    """
    Diff two ``model_inputs`` dicts into a flat list of changes.

    Args:
        inputs_a: Original model inputs.
        inputs_b: Comparison model inputs.

    Returns:
        List of :class:`AssumptionChange`, in deterministic order.
    """
    changes: List[AssumptionChange] = []
    _diff_dict(inputs_a or {}, inputs_b or {}, [], changes)
    return changes


def count_by_status(changes: List[AssumptionChange]) -> Dict[str, int]:
    """Return status -> count mapping (all statuses present, zero-filled)."""
    counts = {
        STATUS_ADDED: 0,
        STATUS_REMOVED: 0,
        STATUS_MODIFIED: 0,
        STATUS_UNCHANGED: 0,
    }
    for change in changes:
        counts[change.status] = counts.get(change.status, 0) + 1
    return counts
