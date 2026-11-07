"""
SBI Hub visual theme — VtSBDC advisor workspace.

Light content area with a dark navy sidebar, Vermont-inspired teal/green
accents, and a mountain-ridge motif in the header.

Palette:
- Navy        #16324F  sidebar, headings, featured card
- Navy deep   #12263B  sidebar gradients
- Green       #2E7D5B  primary accent, card icons
- Teal        #2AA198  secondary accent
- Mist        #EAF1F4  header background
- Off-white   #F4F7F5  app background

Applied globally by the hub shell. The Financial Modeler module renders
inside this theme; see its own ``custom_styles`` for module-level tweaks.
"""
import streamlit as st

from sbi_hub.shell.icons import icon

PALETTE = {
    "navy": "#16324F",
    "navy_deep": "#12263B",
    "green": "#2E7D5B",
    "teal": "#2AA198",
    "mist": "#EAF1F4",
    "surface": "#FFFFFF",
    "background": "#F4F7F5",
    "text": "#16324F",
    "text_muted": "#5A7184",
    "border": "#DCE6EA",
}

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
        background: linear-gradient(180deg, #16324F 0%, #12263B 100%);
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
    .sbi-nav-item {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        color: #DCE8F0;
        text-decoration: none;
        font-size: 0.92rem;
        padding: 0.5rem 0.7rem;
        border-radius: 8px;
        margin-bottom: 0.15rem;
    }
    a.sbi-nav-item:hover {
        background: #FFFFFF14;
        color: #FFFFFF;
    }
    .sbi-nav-item.sbi-nav-active {
        background: #2E7D5B;
        color: #FFFFFF;
        font-weight: 600;
    }
    .sbi-quick-label {
        color: #7C97AB !important;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0.9rem 0 0.3rem;
    }
    .sbi-quick-link {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        color: #B9CCDA;
        font-size: 0.85rem;
        padding: 0.3rem 0.4rem;
        border-radius: 6px;
    }
    .sbi-quick-link svg {
        flex-shrink: 0;
    }
    .sbi-quick-link a {
        color: #B9CCDA;
        text-decoration: none;
        flex: 1;
    }
    .sbi-quick-link a:hover {
        color: #FFFFFF;
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
        background: #2E7D5B;
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
        background: #2E7D5B;
        color: #FFFFFF;
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
        background: #2E7D5B;
        border-radius: 2px;
        margin-bottom: 1.1rem;
    }

    /* ---------- Module cards ---------- */
    .sbi-card {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #DCE6EA;
        border-radius: 14px;
        padding: 1.35rem 1.3rem 3rem;
        min-height: 11.4rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 3px rgba(22, 50, 79, 0.06);
    }
    .sbi-card-icon {
        color: #2E7D5B;
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
    .sbi-arrow {
        position: absolute;
        right: 1rem;
        bottom: 0.9rem;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        border: 1px solid #C8D8DD;
        color: #7C97AB;
        background: #FFFFFF;
    }
    a.sbi-arrow:hover {
        border-color: #2E7D5B;
        color: #2E7D5B;
        background: #F0F7F3;
    }

    /* Featured card */
    .sbi-card-featured {
        background: linear-gradient(135deg, #16324F 0%, #14425A 60%, #14524A 100%);
        border: none;
    }
    .sbi-card-featured .sbi-card-icon {
        color: #7FD1C8;
    }
    .sbi-card-featured .sbi-card-title {
        color: #FFFFFF;
    }
    .sbi-card-featured .sbi-card-tagline {
        color: #A9C4D4;
    }
    .sbi-card-featured .sbi-arrow {
        border-color: #3D6B86;
        color: #BEE3DC;
        background: transparent;
    }
    a.sbi-card-featured .sbi-arrow:hover,
    .sbi-card-featured a.sbi-arrow:hover {
        border-color: #7FD1C8;
        color: #FFFFFF;
        background: #FFFFFF14;
    }
    .sbi-featured-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #BEE3DC;
        color: #14524A;
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
        border-left: 3px solid #2AA198;
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
    .sbi-footer .sbi-pines {
        color: #2E7D5B;
        display: inline-flex;
        gap: 2px;
    }
</style>
"""

_MOUNTAIN_SVG = """
<svg class="sbi-mountains" viewBox="0 0 600 120" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 120 L120 45 L200 85 L300 30 L400 80 L480 40 L600 90 L600 120 Z" fill="#B7CFDD" opacity="0.55"/>
  <path d="M0 120 L90 75 L190 105 L320 55 L430 100 L540 65 L600 95 L600 120 Z" fill="#8FB6C4" opacity="0.5"/>
  <path d="M330 120 L390 88 L430 105 L470 78 L520 108 L560 85 L600 105 L600 120 Z" fill="#5E93A8" opacity="0.45"/>
  <g fill="#2E7D5B" opacity="0.5">
    <path d="M455 120 l6-16 6 16z"/><path d="M470 120 l5-13 5 13z"/><path d="M485 120 l7-19 7 19z"/>
    <path d="M502 120 l5-14 5 14z"/><path d="M516 120 l6-17 6 17z"/><path d="M533 120 l5-12 5 12z"/>
    <path d="M546 120 l7-18 7 18z"/><path d="M562 120 l5-13 5 13z"/><path d="M576 120 l6-16 6 16z"/>
    <path d="M592 120 l5-14 5 14z"/>
  </g>
</svg>
"""


def apply():
    """Inject the SBI Hub global styles."""
    st.markdown(_CSS, unsafe_allow_html=True)


def header_bar():
    """Render the 'Advisor Workspace' header bar with mountain motif."""
    st.markdown(
        '<div class="sbi-header">'
        '<div class="sbi-header-left">'
        '<div class="sbi-header-mark">'
        '<span style="height:14px"></span><span style="height:22px"></span><span style="height:30px"></span>'
        "</div>"
        "<div>"
        '<div class="sbi-header-title">Small Business Intelligence Hub</div>'
        '<div class="sbi-header-sub">Advisor Workspace</div>'
        "</div>"
        "</div>"
        '<div class="sbi-header-right">'
        f'<span class="sbi-header-ico">{icon("help", color="#4A6A82", size=20)}</span>'
        f'<span class="sbi-header-ico">{icon("bell", color="#4A6A82", size=20)}</span>'
        '<span class="sbi-advisor"><span class="sbi-avatar">AD</span>Advisor</span>'
        "</div>"
        + _MOUNTAIN_SVG +
        "</div>",
        unsafe_allow_html=True,
    )
