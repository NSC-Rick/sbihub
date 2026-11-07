"""
SBI Hub — Small Business Intelligence Hub.

Application shell entry point. Owns page configuration and routes between
the landing page and specialized advisory modules.
"""
import streamlit as st

from sbi_hub.config.modules import MODULES, STATUS_ACTIVE, get_module
from sbi_hub.shell import landing, theme

st.set_page_config(
    page_title="SBI Hub",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.apply()

if "active_view" not in st.session_state:
    st.session_state.active_view = "hub"

# ---------------- Sidebar navigation ----------------
st.sidebar.markdown("## 🧭 SBI Hub")
st.sidebar.caption("Small Business Intelligence Hub")

view_ids = ["hub"] + [m["id"] for m in MODULES]
labels = {"hub": "🏠 Hub Home"}
labels.update({m["id"]: f'{m["icon"]} {m["name"]}' for m in MODULES})

if st.session_state.get("nav") not in view_ids:
    st.session_state.nav = st.session_state.active_view


def _sync_nav():
    st.session_state.active_view = st.session_state.nav


def _go_home():
    st.session_state.active_view = "hub"
    st.session_state.nav = "hub"


st.sidebar.radio(
    "Navigate",
    view_ids,
    format_func=lambda v: labels[v],
    key="nav",
    on_change=_sync_nav,
)
st.sidebar.divider()

# ---------------- Router ----------------
active = st.session_state.active_view
module = get_module(active)

if active == "hub" or module is None:
    landing.render()
elif module["status"] == STATUS_ACTIVE and module["id"] == "financial_modeler":
    st.sidebar.button("← Back to SBI Hub", use_container_width=True, on_click=_go_home)

    from sbi_hub.modules.financial_modeler import app as financial_modeler_app
    financial_modeler_app.render()
else:
    landing.render_coming_soon(module)
