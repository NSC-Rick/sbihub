"""
SBI Hub module registry.

Each entry describes one hub module: its identity, card content for the
landing page, icon key (see ``sbi_hub/shell/icons.py``), and availability
status. Adding a future module only requires updating ``status`` and
wiring its entry point in the router (see the repository root ``app.py``).
"""

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
    },
    {
        "id": "idea_feasibility",
        "name": "Business Idea & Feasibility",
        "icon": "bulb",
        "tagline": "Evaluate the strength and readiness of a new idea",
        "description": (
            "Startup costs, break-even, runway, and market readiness before "
            "committing time and capital."
        ),
        "status": STATUS_COMING_SOON,
    },
    {
        "id": "valuation_succession",
        "name": "Business Valuation & Succession",
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
        "tagline": "Where automation and AI pay off first",
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
