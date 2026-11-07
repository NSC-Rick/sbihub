"""
SBI Hub brand configuration.

All sponsor/organization branding lives in this single file: the sidebar
logo mark, organization name and subtitle, the product name, browser-tab
title/icon, the header-bar decorative artwork, and the brand accent
colors. Neutral structural colors (surface, borders, body text) live in
``sbi_hub/shell/theme.py`` and are shared across brands.

To rebrand the hub (e.g. switch to a VtSBDC identity), update ``BRAND``
— no component, template, or CSS changes are required. Provide either an
inline SVG for ``logo_svg``/``header_art_svg`` or extend the loaders to
read image files; ``page_icon`` accepts an emoji or an image path (it is
passed straight to ``st.set_page_config``).

Layered identity: the sponsor organization brands the shell chrome
(sidebar logo block, accents); the product — Small Business
Intelligence Hub — owns the header bar and page title.
"""

_STAR_LOGO_SVG = (
    '<svg width="30" height="30" viewBox="0 0 30 30" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M15 1 L18 12 L29 15 L18 18 L15 29 L12 18 L1 15 L12 12 Z" '
    'fill="#C9A227"/>'
    '<circle cx="15" cy="15" r="2.2" fill="#F0D878"/>'
    '<circle cx="24" cy="6" r="1.1" fill="#F0D878"/>'
    '<circle cx="6" cy="24" r="1.1" fill="#F0D878"/>'
    "</svg>"
)

# Subtle starfield/north-star motif rendered at the right of the header bar
# (replaces the VtSBDC mountain ridge).
_STAR_HEADER_ART_SVG = """
<svg class="sbi-mountains" viewBox="0 0 600 120" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
  <g fill="#C9A227">
    <path d="M470 30 L477.5 52.5 L500 60 L477.5 67.5 L470 90 L462.5 67.5 L440 60 L462.5 52.5 Z" opacity="0.55"/>
    <path d="M540 62 L544 74 L556 78 L544 82 L540 94 L536 82 L524 78 L536 74 Z" opacity="0.4"/>
    <path d="M395 58 L398.2 66.8 L407 70 L398.2 73.2 L395 82 L391.8 73.2 L383 70 L391.8 66.8 Z" opacity="0.35"/>
  </g>
  <g fill="#8FB6C4">
    <circle cx="330" cy="96" r="2" opacity="0.5"/><circle cx="365" cy="40" r="1.6" opacity="0.45"/>
    <circle cx="420" cy="100" r="2.4" opacity="0.5"/><circle cx="510" cy="30" r="1.8" opacity="0.45"/>
    <circle cx="565" cy="104" r="2.2" opacity="0.5"/><circle cx="300" cy="62" r="1.5" opacity="0.4"/>
  </g>
</svg>
"""

BRAND = {
    # ---- Sponsor / organization identity ----
    "org_name": "North Star Consulting",
    "org_subtitle": "Advisory Platform",
    "logo_svg": _STAR_LOGO_SVG,
    # ---- Product identity ----
    "product_name": "Small Business Intelligence Hub",
    "product_subtitle": "Advisor Workspace",
    "app_title": "SBI Hub — North Star Consulting",
    "page_icon": "⭐",
    "tagline": "Better Insights. Better Decisions. Stronger Businesses.",
    "footer_icon": "star",
    "header_art_svg": _STAR_HEADER_ART_SVG,
    # ---- Brand accent palette ----
    # North Star default: navy + gold.
    "colors": {
        "accent": "#C9A227",          # primary accent (nav-active, icons, CTAs)
        "accent_dark": "#8F7115",     # accent hover/pressed
        "accent_text": "#16324F",     # text/icons placed on accent fills
        "accent_soft": "#F0E3B0",     # badge backgrounds
        "accent_soft_text": "#14524A",  # text on accent_soft badges
        "accent_on_dark": "#F0D878",  # accent used on dark surfaces (featured card)
        "sidebar_bg": "#16324F",
        "sidebar_bg_deep": "#0F2438",
    },
}


def get_brand():
    """Return the active brand dictionary."""
    return BRAND
