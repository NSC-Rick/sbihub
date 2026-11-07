"""
SBI Hub module registry.

Each entry describes one hub module: its identity, card content for the
landing page, icon key (see ``sbi_hub/shell/icons.py``), availability
status, and — for active modules — one of two launch modes:

- ``entry_point``: ``"package.module:callable"`` — rendered embedded
  inside the hub shell by the router (see the repository root
  ``app.py``). Good for small tools that belong inside the workspace.
- ``launch_url``: a path (e.g. ``"/fm"``) served by ``serve.py`` —
  opens the module's standalone app in a new browser tab, with its own
  theme, chrome, and session. Used by the Financial Modeler.

Activating a future module requires only setting ``status`` to
``"active"`` and providing one of those fields; no router changes.
"""
import importlib

STATUS_ACTIVE = "active"
STATUS_COMING_SOON = "coming_soon"

MODULES = [
    {
        "id": "financial_modeler",
        "name": "Financial Modeler",
        "icon": "chart",
        "tagline": "Financial performance, cash flow, pricing, and resilience",
        "description": (
            "Create multi-year operating models with revenue streams, payroll, "
            "expenses, financing, and full financial statements."
        ),
        "status": STATUS_ACTIVE,
        "featured": True,
        "launch_url": "/fm",
    },
    {
        "id": "idea_feasibility",
        "name": "Business Idea & Feasibility",
        "icon": "bulb",
        "tagline": "Evaluate the strength and readiness of a new idea",
        "description": (
            "Assess market fit, startup requirements, and viability before "
            "committing time and capital."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "valuation_succession",
        "name": "Business Valuation",
        "icon": "scale",
        "tagline": "Value range, succession, and exit scenarios",
        "description": (
            "Estimate business value and plan for ownership transition or sale."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "workforce_hiring",
        "name": "Workforce & Hiring",
        "icon": "users",
        "tagline": "Hiring, labor costs, and staffing decisions",
        "description": (
            "Model roles, compensation, and hiring timelines against growth plans."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "capital_investment",
        "name": "Capital Investment",
        "icon": "tractor",
        "tagline": "Equipment, leasing, and purchase decisions",
        "description": (
            "Compare equipment, expansion, and financing options side by side."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "sales_growth",
        "name": "Sales & Growth",
        "icon": "growth",
        "tagline": "Leads, conversion, and customer growth",
        "description": (
            "Analyze sales channels, pricing, and growth scenarios for the business."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "operations_modeler",
        "name": "Operations Modeler",
        "icon": "gear",
        "tagline": "Inventory, efficiency, and capacity",
        "description": (
            "Model capacity, workflows, and operational efficiency improvements."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "automation_ai",
        "name": "Automation & AI Opportunity Evaluator",
        "icon": "cpu",
        "tagline": "Find where automation pays off",
        "description": (
            "Identify and prioritize automation and AI opportunities in the business."
        ),
        "status": STATUS_COMING_SOON,
    },
]


def get_module(module_id):
    """Return the module dict for ``module_id`` or ``None`` if unknown."""
    for module in MODULES:
        if module["id"] == module_id:
            return module
    return None


def resolve_entry_point(module):
    """Return the render callable named by ``module``'s ``entry_point`` spec.

    Specs use the form ``"package.module:callable"``. Returns ``None`` when
    the module declares no entry point. Import or attribute errors are left
    to propagate so a misconfigured registry fails loudly rather than
    silently falling back.
    """
    spec = module.get("entry_point")
    if not spec:
        return None
    module_path, _, func_name = spec.partition(":")
    return getattr(importlib.import_module(module_path), func_name)
