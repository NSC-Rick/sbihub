"""
SBI Hub landing page.

Renders the welcome hero, the announcements panel, and the module card
grid. Active modules navigate into the module router; upcoming modules
are labeled Coming Soon.
"""
import streamlit as st

from sbi_hub.config.modules import MODULES, STATUS_ACTIVE
from sbi_hub.shell import announcements

TAGLINE = "Better Insights. Better Decisions. Stronger Businesses."


def _open_module(module_id):
    st.session_state.active_view = module_id
    st.session_state.nav = module_id
    st.session_state._scroll_to_top = True


def _render_hero():
    st.markdown(
        '<div class="sbi-hero">'
        "<h1>Welcome to SBI Hub</h1>"
        f'<div class="sbi-tagline">{TAGLINE}</div>'
        '<p class="sbi-intro">'
        "Your central workspace for small-business advising. SBI Hub brings "
        "financial modeling, feasibility analysis, valuation, workforce planning, "
        "and more together in one place — so every client conversation starts "
        "with better information."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_card(module, column):
    active = module["status"] == STATUS_ACTIVE
    card_class = "sbi-card sbi-card-active" if active else "sbi-card"
    badge = (
        '<span class="sbi-badge sbi-badge-active">AVAILABLE</span>'
        if active
        else '<span class="sbi-badge sbi-badge-soon">COMING SOON</span>'
    )

    with column:
        st.markdown(
            f'<div class="{card_class}">'
            f'<div class="sbi-card-icon">{module["icon"]}</div>'
            f'<div class="sbi-card-title">{module["name"]}</div>'
            f'<div class="sbi-card-tagline">{module["tagline"]}</div>'
            f'<div class="sbi-card-desc">{module["description"]}</div>'
            f"{badge}"
            "</div>",
            unsafe_allow_html=True,
        )
        if active:
            st.button(
                f"Open {module['name']}",
                key=f"open_{module['id']}",
                type="primary",
                use_container_width=True,
                on_click=_open_module,
                args=(module["id"],),
            )
        else:
            st.button(
                "Coming Soon",
                key=f"soon_{module['id']}",
                disabled=True,
                use_container_width=True,
            )


def render():
    """Render the SBI Hub landing page."""
    _render_hero()

    announcements.render()

    st.markdown("### 🧰 Advisory Modules")

    columns_per_row = 4
    for row_start in range(0, len(MODULES), columns_per_row):
        row = MODULES[row_start:row_start + columns_per_row]
        cols = st.columns(columns_per_row, gap="medium")
        for col, module in zip(cols, row):
            _render_card(module, col)


def render_coming_soon(module):
    """Render a placeholder page for a module still in development."""
    st.markdown(
        '<div class="sbi-hero">'
        f'<h1>{module["icon"]} {module["name"]}</h1>'
        f'<div class="sbi-tagline">{module["tagline"]}</div>'
        f'<p class="sbi-intro">{module["description"]}</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.info("This module is under development and will be available in a future build.")

    def _go_home():
        st.session_state.active_view = "hub"
        st.session_state.nav = "hub"

    st.button("← Back to SBI Hub", on_click=_go_home)
