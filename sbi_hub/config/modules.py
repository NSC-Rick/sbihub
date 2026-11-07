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
        "tagline": (
            "Financial projections, cash flow, profitability, and "
            "scenario analysis."
        ),
        "description": (
            "Financial projections, cash flow, profitability, and "
            "scenario analysis."
        ),
        "status": STATUS_ACTIVE,
        "featured": True,
        "launch_url": "/fm",
    },
    {
        "id": "idea_feasibility",
        "name": "Business Idea Feasibility & Startup",
        "icon": "bulb",
        "tagline": (
            "Evaluate business ideas, assess market potential, and test "
            "startup viability."
        ),
        "description": (
            "Evaluate business ideas, assess market potential, and test "
            "startup viability."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "valuation_succession",
        "name": "Business Valuation & Succession",
        "icon": "scale",
        "tagline": (
            "Estimate business value, explore exit scenarios, and plan "
            "ownership transitions."
        ),
        "description": (
            "Estimate business value, explore exit scenarios, and plan "
            "ownership transitions."
        ),
        "status": STATUS_ACTIVE,
        "featured": True,
        "badge": "PILOT",
        "launch_url": "https://valuation-wesj.onrender.com/",
    },
    {
        "id": "workforce_hiring",
        "name": "Workforce & Hiring Decisions",
        "icon": "users",
        "tagline": (
            "Evaluate staffing needs, labor costs, productivity, and "
            "hiring alternatives."
        ),
        "description": (
            "Evaluate staffing needs, labor costs, productivity, and "
            "hiring alternatives."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "capital_investment",
        "name": "Projects and Capital Investments",
        "icon": "tractor",
        "tagline": (
            "Evaluate business projects, equipment investments, financing "
            "options, and returns."
        ),
        "description": (
            "Evaluate business projects, equipment investments, financing "
            "options, and returns."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "sales_growth",
        "name": "Sales & Growth",
        "icon": "growth",
        "tagline": (
            "Model customer acquisition, sales performance, revenue growth, "
            "and marketing effectiveness."
        ),
        "description": (
            "Model customer acquisition, sales performance, revenue growth, "
            "and marketing effectiveness."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "operations_modeler",
        "name": "Operations & Efficiency",
        "icon": "gear",
        "tagline": (
            "Improve inventory management, operating efficiency, and "
            "business capacity."
        ),
        "description": (
            "Improve inventory management, operating efficiency, and "
            "business capacity."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "automation_ai",
        "name": "Automation & AI Opportunities",
        "icon": "cpu",
        "tagline": (
            "Identify automation opportunities, evaluate AI use cases, and "
            "estimate potential business value."
        ),
        "description": (
            "Identify automation opportunities, evaluate AI use cases, and "
            "estimate potential business value."
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
