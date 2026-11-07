"""
SBI Hub — Small Business Intelligence Hub.

Application shell entry point. Owns page configuration, the advisor-workspace
sidebar, and routing between the landing page, workspace views, and
specialized advisory modules.

Navigation is session-state based: sidebar nav buttons and embedded
module-card controls update ``st.session_state.active_view`` inside a
normal rerun, so no in-progress state is lost to a page reload. The
``?view=<id>`` query parameter remains supported as a deep-link entry
point only. Hub-level view ids are ``hub``, ``clients``, ``scenarios``,
and ``notes``; module view ids come from the module registry. Active
modules either embed via their ``entry_point`` or launch as standalone
apps in a new tab via ``launch_url`` (served by ``serve.py``).
"""
import streamlit as st

from sbi_hub.config.branding import get_brand
from sbi_hub.config.modules import (
    STATUS_ACTIVE,
    get_module,
    resolve_entry_point,
)
from sbi_hub.shell import landing, theme

BRAND = get_brand()

st.set_page_config(
    page_title=BRAND["app_title"],
    page_icon=BRAND["page_icon"],
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

# ---- Query-parameter deep links (entry point only) ----
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


def _set_view(view_id):
    st.session_state.active_view = view_id


def _go_home():
    st.session_state.active_view = "hub"


# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(
        f'{BRAND["logo_svg"]}'
        f'<div class="sbi-logo-title">{BRAND["org_name"]}</div>'
        f'<div class="sbi-logo-sub">{BRAND["org_subtitle"]}</div>'
        '<div class="sbi-quick-label">Workspace</div>',
        unsafe_allow_html=True,
    )
    theme.nav_icon_styles({view_id: ic for view_id, (_, ic) in HUB_VIEWS.items()})

    for view_id, (label, _ic) in HUB_VIEWS.items():
        with st.container(key=f"sbinav_{view_id}"):
            st.button(
                label,
                key=f"nav_{view_id}",
                type="primary" if view_id == active else "secondary",
                use_container_width=True,
                on_click=_set_view,
                args=(view_id,),
            )

    if active != "hub" and module is not None:
        st.divider()
        st.button("← Back to SBI Hub", use_container_width=True, on_click=_go_home)

# ---------------- Router ----------------
if active != "hub" and active in HUB_VIEWS:
    landing.render_hub_view(active)
elif active == "hub" or module is None:
    landing.render()
elif module["status"] != STATUS_ACTIVE:
    landing.render_coming_soon(module)
elif module.get("entry_point"):
    resolve_entry_point(module)()
elif module.get("launch_url"):
    landing.render_external(module)
else:
    st.error(
        f"Module '{module['name']}' is marked active but has no entry point "
        "or launch URL."
    )
