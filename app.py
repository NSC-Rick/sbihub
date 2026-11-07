"""
SBI Hub — Small Business Intelligence Hub.

Application shell entry point. Owns page configuration, the advisor-workspace
sidebar, and routing between the landing page, workspace views, and
specialized advisory modules.

Navigation is driven by ``?view=<id>`` query parameters: module cards,
sidebar nav items, and quick-access links all resolve through the router
below. Hub-level view ids are ``hub``, ``clients``, ``scenarios``, and
``notes``; module view ids come from the module registry.
"""
import streamlit as st

from sbi_hub.config.modules import MODULES, STATUS_ACTIVE, get_module
from sbi_hub.shell import landing, theme
from sbi_hub.shell.icons import icon

st.set_page_config(
    page_title="SBI Hub",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.apply()
st.session_state["sbi_theme"] = "light"

HUB_VIEWS = {
    "hub": ("Home", "home"),
    "clients": ("Recent Clients", "users"),
    "scenarios": ("Saved Scenarios", "folder"),
    "notes": ("Advisor Notes", "note"),
}

# ---- Query-parameter navigation ----
view_param = st.query_params.get("view")
if view_param:
    del st.query_params["view"]
    if view_param in HUB_VIEWS or get_module(view_param):
        st.session_state.active_view = view_param
    st.rerun()

if "active_view" not in st.session_state:
    st.session_state.active_view = "hub"

active = st.session_state.active_view
module = get_module(active)


def _go_home():
    st.session_state.active_view = "hub"


# ---------------- Sidebar ----------------
_LOGO_SVG = (
    '<svg width="34" height="26" viewBox="0 0 34 26" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M2 24 L11 9 L16 17 L22 5 L32 24 Z" fill="#4C9F70"/>'
    '<path d="M18 24 L25 12 L32 24 Z" fill="#7FD1C8" opacity="0.8"/></svg>'
)

with st.sidebar:
    st.markdown(
        f"{_LOGO_SVG}"
        '<div class="sbi-logo-title">VtSBDC</div>'
        '<div class="sbi-logo-sub">Vermont Small Business<br>Development Center</div>',
        unsafe_allow_html=True,
    )

    nav_html = ""
    for view_id, (label, ic) in HUB_VIEWS.items():
        cls = "sbi-nav-item sbi-nav-active" if view_id == active else "sbi-nav-item"
        nav_html += (
            f'<a class="{cls}" href="?view={view_id}" target="_self">'
            f'{icon(ic, size=17)}{label}</a>'
        )
    st.markdown(nav_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="sbi-quick-label">Quick Access</div>'
        f'<div class="sbi-quick-link">{icon("users", size=15)}'
        '<a href="?view=clients" target="_self">Recent Clients</a>'
        f'{icon("chevron", size=13)}</div>'
        f'<div class="sbi-quick-link">{icon("folder", size=15)}'
        '<a href="?view=scenarios" target="_self">Saved Scenarios</a>'
        f'{icon("chevron", size=13)}</div>'
        f'<div class="sbi-quick-link">{icon("note", size=15)}'
        '<a href="?view=notes" target="_self">Advisor Notes</a>'
        f'{icon("chevron", size=13)}</div>',
        unsafe_allow_html=True,
    )

    if active != "hub" and module is not None:
        st.divider()
        st.button("← Back to SBI Hub", use_container_width=True, on_click=_go_home)

# ---------------- Router ----------------
if active in ("clients", "scenarios", "notes"):
    landing.render_hub_view(active)
elif active == "hub" or module is None:
    landing.render()
elif module["status"] == STATUS_ACTIVE and module["id"] == "financial_modeler":
    from sbi_hub.modules.financial_modeler import app as financial_modeler_app
    financial_modeler_app.render()
else:
    landing.render_coming_soon(module)
