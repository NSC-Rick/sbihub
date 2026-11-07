"""
SBI Hub visual theme — workspace shell.

Light content area with a dark sidebar and brand-accented chrome. All
sponsor/organization branding (logo art, names, accent colors, header
artwork) comes from ``sbi_hub/config/branding.py``; this file owns only
the neutral structure: surfaces, borders, body text, and layout styling.

Brand color placeholders (``%%TOKEN%%``) in ``_CSS`` are substituted by
``apply()`` with the active brand palette — rebrand by editing the
config, not this file.
"""
import base64

import streamlit as st

from sbi_hub.config.branding import get_brand
from sbi_hub.shell.icons import icon


_CSS = """
<style>
    /* ---------- App chrome ---------- */
    .stApp {
        background-color: #F4F7F5;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 1.25rem;
        max-width: 76rem;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, %%SIDEBAR_BG%% 0%, %%SIDEBAR_BG_DEEP%% 100%);
        border-right: none;
    }
    section[data-testid="stSidebar"] * {
        color: #DCE8F0;
    }
    section[data-testid="stSidebar"] .sbi-logo-title {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        line-height: 1.1;
    }
    section[data-testid="stSidebar"] .sbi-logo-sub {
        color: #9FB8C9;
        font-size: 0.68rem;
        line-height: 1.25;
        margin-bottom: 0.9rem;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #2A4763;
    }
    .sbi-quick-label {
        color: #7C97AB !important;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0.55rem 0 0.3rem;
    }

    /* Sidebar nav — Streamlit buttons inside keyed wrappers (sbinav_<view>),
       styled to match the mockup nav pills. Icons are injected per view by
       nav_icon_styles() as ::before data-URI images. */
    [class*="st-key-sbinav_"] {
        margin-bottom: 0.15rem;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button {
        justify-content: flex-start;
        gap: 0.65rem;
        background: transparent;
        border: none;
        color: #DCE8F0;
        font-size: 0.92rem;
        font-weight: 400;
        padding: 0.5rem 0.7rem;
        border-radius: 8px;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button > div {
        justify-content: flex-start;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button p {
        text-align: left;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button:hover {
        background: #FFFFFF14;
        color: #FFFFFF;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button:focus:not(:active) {
        color: #FFFFFF;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button[kind="primary"],
    [class*="st-key-sbinav_"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
        background: %%ACCENT%%;
        color: %%ACCENT_TEXT%%;
        font-weight: 600;
    }
    [class*="st-key-sbinav_"] [data-testid="stButton"] button[kind="primary"]:hover,
    [class*="st-key-sbinav_"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover {
        background: %%ACCENT%%;
        color: %%ACCENT_TEXT%%;
    }
    section[data-testid="stSidebar"] [data-testid="stAlert"] * {
        color: #16324F;
    }

    /* ---------- Header bar ---------- */
    .sbi-header {
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        background: linear-gradient(120deg, #E9F0F4 0%, #E3EEF0 55%, #DCEAE4 100%);
        border: 1px solid #D7E3E8;
        border-radius: 14px;
        padding: 1.1rem 1.5rem 0;
        min-height: 5.6rem;
        margin-bottom: 1.4rem;
    }
    .sbi-header-left {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        z-index: 1;
    }
    .sbi-header-mark {
        display: flex;
        align-items: flex-end;
        gap: 3px;
        padding-bottom: 2px;
    }
    .sbi-header-mark span {
        display: block;
        width: 7px;
        background: %%ACCENT%%;
        border-radius: 2px 2px 0 0;
    }
    .sbi-header-title {
        color: #16324F;
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1.15;
    }
    .sbi-header-sub {
        color: #5A7184;
        font-size: 0.82rem;
    }
    .sbi-header-right {
        display: flex;
        align-items: center;
        gap: 1rem;
        z-index: 1;
        padding-top: 0.35rem;
    }
    .sbi-header-ico {
        color: #4A6A82;
        display: inline-flex;
    }
    .sbi-advisor {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #16324F;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .sbi-avatar {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        background: %%ACCENT%%;
        color: %%ACCENT_TEXT%%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .sbi-mountains {
        position: absolute;
        right: 0;
        bottom: 0;
        left: 30%;
        height: 100%;
        pointer-events: none;
    }

    /* ---------- Welcome heading ---------- */
    .sbi-welcome h2 {
        color: #16324F;
        font-size: 1.55rem;
        font-weight: 800;
        margin: 0 0 0.25rem;
    }
    .sbi-welcome .sbi-welcome-sub {
        color: #5A7184;
        font-size: 0.95rem;
        margin: 0 0 0.4rem;
    }
    .sbi-welcome .sbi-underline {
        width: 3.2rem;
        height: 3px;
        background: %%ACCENT%%;
        border-radius: 2px;
        margin-bottom: 1.1rem;
    }

    /* ---------- Module cards ---------- */
    [class*="st-key-card_"] {
        height: 100%;
    }
    .sbi-card {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #DCE6EA;
        border-radius: 14px;
        padding: 1.35rem 1.3rem 3rem;
        min-height: 11.4rem;
        height: calc(100% - 0.9rem);
        box-sizing: border-box;
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 3px rgba(22, 50, 79, 0.06);
    }
    /* Equal-height cards — stretch the wrapper chain from the column
       (flex-stretched to the row height) down to the card element. */
    [data-testid="stColumn"]:has([class*="st-key-card_"])
        > [data-testid="stVerticalBlock"],
    [data-testid="stColumn"]:has([class*="st-key-card_"])
        > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"],
    [class*="st-key-card_"]
        > [data-testid="stElementContainer"]:has(.sbi-card),
    [class*="st-key-card_"]
        > [data-testid="stElementContainer"]:has(.sbi-card) > .stMarkdown,
    [class*="st-key-card_"]
        > [data-testid="stElementContainer"]:has(.sbi-card) > .stMarkdown > div,
    [class*="st-key-card_"]
        > [data-testid="stElementContainer"]:has(.sbi-card)
        [data-testid="stMarkdownContainer"] {
        height: 100%;
    }
    /* Keep the absolute-positioned launch link's element container out
       of the card block's flex layout so card heights stay uniform. */
    [class*="st-key-card_"] {
        gap: 0;
    }
    [class*="st-key-card_"]
        > [data-testid="stElementContainer"]:not(:has(.sbi-card)) {
        display: contents;
    }
    /* Card grid — wrap to two columns on narrower viewports */
    @media (max-width: 1150px) {
        [data-testid="stHorizontalBlock"]:has([class*="st-key-card_"]) {
            flex-wrap: wrap;
            row-gap: 0.5rem;
        }
        [data-testid="stHorizontalBlock"]:has([class*="st-key-card_"])
        > [data-testid="stColumn"] {
            flex: 1 1 45%;
            min-width: 240px;
        }
    }
    .sbi-card-icon {
        color: %%ACCENT%%;
        margin-bottom: 0.7rem;
    }
    .sbi-card-title {
        color: #16324F;
        font-weight: 700;
        font-size: 1.05rem;
        line-height: 1.25;
        margin-bottom: 0.3rem;
    }
    .sbi-card-tagline {
        color: #5A7184;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    /* Card action button — a Streamlit button (keyed open_<module>) whose
       element container is overlaid where the mockup's circular arrow
       sits; only rendered on active module cards. */
    [class*="st-key-card_"] {
        position: relative;
    }
    [class*="st-key-open_"] {
        position: absolute !important;
        right: 1rem;
        bottom: 0.9rem;
        width: auto !important;
        margin: 0;
    }
    [class*="st-key-open_"] button {
        width: 2rem;
        height: 2rem;
        min-height: 0;
        padding: 0;
        border-radius: 50%;
        border: 1px solid #C8D8DD;
        color: #7C97AB;
        background: #FFFFFF;
        font-size: 0.95rem;
        line-height: 1;
    }
    [class*="st-key-open_"] button:hover {
        border-color: %%ACCENT%%;
        color: %%ACCENT%%;
        background: #F0F7F3;
    }
    [class*="st-key-card_"]:has(.sbi-card-featured) [class*="st-key-open_"] button {
        border-color: #3D6B86;
        color: %%ACCENT_SOFT%%;
        background: transparent;
    }
    [class*="st-key-card_"]:has(.sbi-card-featured) [class*="st-key-open_"] button:hover {
        border-color: %%ACCENT_ON_DARK%%;
        color: #FFFFFF;
        background: #FFFFFF14;
    }

    /* External-launch link — same circle, anchored the same way, but a
       real <a target="_blank"> for modules served as standalone apps. */
    [class*="st-key-card_"] a.sbi-open-link {
        position: absolute;
        right: 1rem;
        bottom: 0.9rem;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #C8D8DD;
        color: #7C97AB;
        background: #FFFFFF;
        text-decoration: none;
        z-index: 2;
    }
    [class*="st-key-card_"] a.sbi-open-link:hover {
        border-color: %%ACCENT%%;
        color: %%ACCENT%%;
        background: #F0F7F3;
    }
    [class*="st-key-card_"]:has(.sbi-card-featured) a.sbi-open-link {
        border-color: #3D6B86;
        color: %%ACCENT_SOFT%%;
        background: transparent;
    }
    [class*="st-key-card_"]:has(.sbi-card-featured) a.sbi-open-link:hover {
        border-color: %%ACCENT_ON_DARK%%;
        color: #FFFFFF;
        background: #FFFFFF14;
    }
    .sbi-card-note {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        margin-top: 0.55rem;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .sbi-card-featured .sbi-card-note {
        color: %%ACCENT_ON_DARK%%;
    }
    .sbi-card:not(.sbi-card-featured) .sbi-card-note {
        color: #7C97AB;
    }

    /* Launch CTA on the external-module launcher page */
    a.sbi-launch-cta {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: %%ACCENT%%;
        color: %%ACCENT_TEXT%%;
        font-weight: 600;
        font-size: 0.92rem;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        margin: 0.4rem 0 0.6rem;
    }
    a.sbi-launch-cta:hover {
        background: %%ACCENT_DARK%%;
        color: %%ACCENT_TEXT%%;
    }

    /* Featured card */
    .sbi-card-featured {
        background: linear-gradient(135deg, #16324F 0%, #14425A 60%, #14524A 100%);
        border: none;
    }
    .sbi-card-featured .sbi-card-icon {
        color: %%ACCENT_ON_DARK%%;
    }
    .sbi-card-featured .sbi-card-title {
        color: #FFFFFF;
    }
    .sbi-card-featured .sbi-card-tagline {
        color: #A9C4D4;
    }
    .sbi-featured-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: %%ACCENT_SOFT%%;
        color: %%ACCENT_SOFT_TEXT%%;
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        padding: 3px 9px;
        border-radius: 9px;
    }

    /* Coming-soon card — visibly inert: no arrow, muted, dashed border */
    .sbi-card-soon {
        background: #F8FAFA;
        border-style: dashed;
        box-shadow: none;
    }
    .sbi-card-soon .sbi-card-icon {
        color: #9DB4C0;
    }
    .sbi-card-soon .sbi-card-title {
        color: #5A7184;
    }
    .sbi-soon-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #EDF2F4;
        border: 1px solid #DCE6EA;
        color: #7C97AB;
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        padding: 3px 9px;
        border-radius: 9px;
    }

    /* ---------- Announcements ---------- */
    .sbi-announcement {
        background: #FFFFFF;
        border: 1px solid #DCE6EA;
        border-left: 3px solid %%ACCENT%%;
        border-radius: 8px;
        padding: 0.55rem 0.9rem;
        margin-bottom: 0.45rem;
    }
    .sbi-announcement-meta {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.1rem;
    }
    .sbi-announcement-date {
        color: #7C97AB;
        font-size: 0.73rem;
    }
    .sbi-announcement-title {
        color: #16324F;
        font-weight: 600;
        font-size: 0.92rem;
    }
    .sbi-announcement-desc {
        color: #5A7184;
        font-size: 0.83rem;
    }

    /* ---------- Footer ---------- */
    .sbi-footer {
        background: #E4EDF1;
        border: 1px solid #D7E3E8;
        border-radius: 10px;
        text-align: center;
        color: #16324F;
        font-weight: 600;
        font-style: italic;
        padding: 0.75rem 1rem;
        margin-top: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.7rem;
    }
    .sbi-footer .sbi-brandmark {
        color: %%ACCENT%%;
        display: inline-flex;
        gap: 2px;
    }
</style>
"""

def apply():
    """Inject the SBI Hub global styles with the active brand palette."""
    css = _CSS
    for key, value in get_brand()["colors"].items():
        css = css.replace(f"%%{key.upper()}%%", value)
    st.markdown(css, unsafe_allow_html=True)


def nav_icon_styles(view_icons):
    """Inject per-view icons for sidebar nav buttons.

    ``view_icons`` maps a view id to an icon name from
    ``sbi_hub.shell.icons``. Each rule targets the keyed wrapper
    ``sbinav_<view_id>`` rendered around the nav button in ``app.py`` and
    draws the SVG as a ``::before`` image, matching the mockup's leading
    icon. Called once per rerun, in the sidebar.
    """
    rules = ["<style>"]
    for view_id, icon_name in view_icons.items():
        svg = icon(icon_name, color="#DCE8F0", size=17)
        encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        rules.append(
            f".st-key-sbinav_{view_id} [data-testid='stButton'] button::before "
            "{ content:''; flex:none; width:17px; height:17px; "
            f"background:url('data:image/svg+xml;base64,{encoded}') "
            "center/contain no-repeat; }"
        )
    rules.append("</style>")
    st.markdown("".join(rules), unsafe_allow_html=True)


def header_bar():
    """Render the product header bar with the brand's decorative artwork."""
    brand = get_brand()
    st.markdown(
        '<div class="sbi-header">'
        '<div class="sbi-header-left">'
        '<div class="sbi-header-mark">'
        '<span style="height:14px"></span><span style="height:22px"></span><span style="height:30px"></span>'
        "</div>"
        "<div>"
        f'<div class="sbi-header-title">{brand["product_name"]}</div>'
        f'<div class="sbi-header-sub">{brand["product_subtitle"]}</div>'
        "</div>"
        "</div>"
        '<div class="sbi-header-right">'
        f'<span class="sbi-header-ico">{icon("help", color="#4A6A82", size=20)}</span>'
        f'<span class="sbi-header-ico">{icon("bell", color="#4A6A82", size=20)}</span>'
        '<span class="sbi-advisor"><span class="sbi-avatar">U</span>User</span>'
        "</div>"
        + brand["header_art_svg"] +
        "</div>",
        unsafe_allow_html=True,
    )
