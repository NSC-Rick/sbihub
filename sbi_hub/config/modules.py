"""
SBI Hub module registry.

Each entry describes one hub module: its identity, card content for the
landing page, and availability status. Adding a future module only
requires updating ``status`` and wiring its entry point in the router
(see the repository root ``app.py``).
"""

STATUS_ACTIVE = "active"
STATUS_COMING_SOON = "coming_soon"

MODULES = [
    {
        "id": "financial_modeler",
        "name": "Financial Modeler",
        "icon": "💰",
        "tagline": "Build monthly and annual financial projections.",
        "description": (
            "Create multi-year operating models with revenue streams, payroll, "
            "expenses, financing, and full financial statements."
        ),
        "status": STATUS_ACTIVE,
    },
    {
        "id": "idea_feasibility",
        "name": "Business Idea & Feasibility",
        "icon": "💡",
        "tagline": "Pressure-test a new business idea.",
        "description": (
            "Evaluate market fit, startup requirements, and viability before "
            "committing time and capital."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "valuation_succession",
        "name": "Business Valuation & Succession",
        "icon": "🤝",
        "tagline": "Understand what the business is worth.",
        "description": (
            "Estimate business value and plan for ownership transition or sale."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "workforce_hiring",
        "name": "Workforce & Hiring",
        "icon": "👥",
        "tagline": "Plan the team the business needs.",
        "description": (
            "Model roles, compensation, and hiring timelines against growth plans."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "capital_investment",
        "name": "Capital Investment",
        "icon": "🏦",
        "tagline": "Evaluate major purchases and financing.",
        "description": (
            "Compare equipment, expansion, and financing options side by side."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "sales_growth",
        "name": "Sales & Growth",
        "icon": "📈",
        "tagline": "Chart a path to higher revenue.",
        "description": (
            "Analyze sales channels, pricing, and growth scenarios for the business."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "operations_modeler",
        "name": "Operations Modeler",
        "icon": "⚙️",
        "tagline": "Streamline how the business runs.",
        "description": (
            "Model capacity, workflows, and operational efficiency improvements."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "automation_ai",
        "name": "Automation & AI Opportunity Evaluator",
        "icon": "🤖",
        "tagline": "Find where automation pays off.",
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
