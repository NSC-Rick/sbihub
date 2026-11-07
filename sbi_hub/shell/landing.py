"""
SBI Hub landing page.

Renders the workspace header, the welcome heading, the module
card grid (featured Financial Modeler plus upcoming modules), the
announcements panel, and the footer tagline.

Active module cards either expose a Streamlit button that updates
``st.session_state.active_view`` in-place (embedded modules), or an
``<a target="_blank">`` link for modules that launch their own
standalone app in a new browser tab (``launch_url`` in the registry).
"""
import streamlit as st

from sbi_hub.config.branding import get_brand
from sbi_hub.config.modules import MODULES, STATUS_ACTIVE
from sbi_hub.shell import announcements, theme
from sbi_hub.shell.icons import icon


def _render_welcome():
    st.markdown(
        '<div class="sbi-welcome">'
        "<h2>What would you like to analyze today?</h2>"
        '<p class="sbi-welcome-sub">'
        "A central hub for analyzing, planning, and making informed "
        "business decisions."
        "</p>"
        '<div class="sbi-underline"></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def _open_module(module_id):
    st.session_state.active_view = module_id
    st.session_state._scroll_to_top = True


def _render_card(module, column):
    featured = module.get("featured")
    active = module["status"] == STATUS_ACTIVE
    if featured:
        classes = "sbi-card sbi-card-featured"
        badge = '<span class="sbi-featured-badge">FEATURED</span>'
    elif active:
        classes, badge = "sbi-card", ""
    else:
        classes = "sbi-card sbi-card-soon"
        badge = '<span class="sbi-soon-badge">COMING SOON</span>'

    launch_url = module.get("launch_url")
    new_tab_note = (
        '<div class="sbi-card-note">'
        f'{icon("external", size=11)}Opens in a new tab</div>'
        if launch_url else ""
    )

    with column, st.container(key=f"card_{module['id']}"):
        st.markdown(
            f'<div class="{classes}">{badge}'
            f'<div class="sbi-card-icon">{icon(module["icon"], size=30)}</div>'
            f'<div class="sbi-card-title">{module["name"]}</div>'
            f'<div class="sbi-card-tagline">{module["tagline"]}</div>'
            f"{new_tab_note}"
            "</div>",
            unsafe_allow_html=True,
        )
        if active and launch_url:
            st.markdown(
                f'<a class="sbi-open-link" href="{launch_url}" target="_blank" '
                f'title="Open {module["name"]} in a new tab">'
                f'{icon("external", size=15)}</a>',
                unsafe_allow_html=True,
            )
        elif active:
            st.button(
                "→",
                key=f"open_{module['id']}",
                help=f"Open {module['name']}",
                on_click=_open_module,
                args=(module["id"],),
            )


def _render_grid():
    columns_per_row = 4
    for row_start in range(0, len(MODULES), columns_per_row):
        row = MODULES[row_start:row_start + columns_per_row]
        cols = st.columns(columns_per_row, gap="medium")
        for col, module in zip(cols, row):
            with col:
                _render_card(module, col)


def _render_footer():
    brand = get_brand()
    mark = icon(brand["footer_icon"], size=18) + icon(brand["footer_icon"], size=14)
    st.markdown(
        f'<div class="sbi-footer"><span class="sbi-brandmark">{mark}</span>'
        f"{brand['tagline']}</div>",
        unsafe_allow_html=True,
    )


def render():
    """Render the SBI Hub landing page."""
    theme.header_bar()
    _render_welcome()
    _render_grid()
    st.markdown("")
    announcements.render()
    _render_footer()


def render_coming_soon(module):
    """Render a placeholder page for a module still in development."""
    theme.header_bar()
    st.markdown(
        f'<div class="sbi-card" style="min-height:0; padding-bottom:1.35rem;">'
        f'<div class="sbi-card-icon">{icon(module["icon"], size=34)}</div>'
        f'<div class="sbi-card-title">{module["name"]}</div>'
        f'<div class="sbi-card-tagline">{module["description"]}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.info("This module is under development and will be available in a future build.")


def render_external(module):
    """Render the launch page for a module that runs as its own app."""
    theme.header_bar()
    launch_url = module["launch_url"]
    st.markdown(
        f'<div class="sbi-card" style="min-height:0; padding-bottom:1.35rem;">'
        f'<div class="sbi-card-icon">{icon(module["icon"], size=34)}</div>'
        f'<div class="sbi-card-title">{module["name"]}</div>'
        f'<div class="sbi-card-tagline">{module["description"]}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<a class="sbi-launch-cta" href="{launch_url}" target="_blank">'
        f'{icon("external", size=15)}Open {module["name"]} in a new tab</a>',
        unsafe_allow_html=True,
    )
    st.caption(
        "This module runs as its own application in a separate tab, "
        "with its original look and an independent session. This hub "
        "page stays open."
    )


def render_hub_view(view):
    """Render a placeholder for workspace views (clients, scenarios, notes)."""
    theme.header_bar()
    titles = {
        "clients": "Recent Clients",
        "scenarios": "Saved Scenarios",
        "notes": "Advisor Notes",
    }
    title = titles.get(view, view.replace("_", " ").title())
    st.markdown(
        f'<div class="sbi-welcome"><h2>{title}</h2><div class="sbi-underline"></div></div>',
        unsafe_allow_html=True,
    )
    st.info("This workspace view is planned for a future build.")
