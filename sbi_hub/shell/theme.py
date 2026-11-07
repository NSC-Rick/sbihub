"""
SBI Hub visual theme — Vermont-inspired navy, teal, and green.

Palette:
- Deep navy   #0E1C2B  app background
- Navy        #17304A  surfaces / cards
- Teal        #2AA198  primary accent
- Green       #4C9F70  secondary accent
- Light navy  #7FA6C9  muted text / borders

Applied globally by the hub shell so the Financial Modeler module
inherits the same look and feel.
"""
import streamlit as st

PALETTE = {
    "navy_deep": "#0E1C2B",
    "navy": "#17304A",
    "navy_light": "#7FA6C9",
    "teal": "#2AA198",
    "green": "#4C9F70",
    "text": "#F2F6FA",
    "text_muted": "#A9BFD4",
}

_CSS = """
<style>
    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background-color: #12263B;
        border-right: 1px solid #1E3A55;
    }

    /* ---------- Hub hero ---------- */
    .sbi-hero {
        background: linear-gradient(135deg, #17304A 0%, #143F45 55%, #1B4D3E 100%);
        border: 1px solid #234E6B;
        border-radius: 14px;
        padding: 2rem 2.25rem 1.5rem;
        margin-bottom: 1.25rem;
    }
    .sbi-hero h1 {
        color: #F2F6FA;
        margin: 0 0 0.35rem 0;
        font-size: 2.1rem;
    }
    .sbi-hero .sbi-tagline {
        color: #7FD1C8;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 0.6rem;
    }
    .sbi-hero .sbi-intro {
        color: #C9DAE8;
        max-width: 60rem;
        margin: 0;
    }

    /* ---------- Announcements ---------- */
    .sbi-announcement {
        background-color: #14273C;
        border: 1px solid #1E3A55;
        border-left: 3px solid #2AA198;
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.5rem;
    }
    .sbi-announcement-meta {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.15rem;
    }
    .sbi-announcement-date {
        color: #7FA6C9;
        font-size: 0.75rem;
    }
    .sbi-announcement-title {
        color: #F2F6FA;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .sbi-announcement-desc {
        color: #A9BFD4;
        font-size: 0.85rem;
    }

    /* ---------- Module cards ---------- */
    .sbi-card {
        background-color: #14273C;
        border: 1px solid #1E3A55;
        border-radius: 12px;
        padding: 1.1rem 1.2rem 0.9rem;
        min-height: 12.5rem;
        margin-bottom: 0.5rem;
    }
    .sbi-card-active {
        border-color: #2AA198;
        box-shadow: 0 0 0 1px #2AA19833, 0 4px 18px rgba(42, 161, 152, 0.12);
    }
    .sbi-card-icon {
        font-size: 1.8rem;
        line-height: 1;
    }
    .sbi-card-title {
        color: #F2F6FA;
        font-weight: 700;
        font-size: 1.02rem;
        margin: 0.45rem 0 0.15rem;
    }
    .sbi-card-tagline {
        color: #7FD1C8;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .sbi-card-desc {
        color: #A9BFD4;
        font-size: 0.83rem;
        min-height: 3.4rem;
    }
    .sbi-badge {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        padding: 2px 9px;
        border-radius: 10px;
    }
    .sbi-badge-active {
        background-color: #2AA198;
        color: #0E1C2B;
    }
    .sbi-badge-soon {
        background-color: #1E3A55;
        color: #A9BFD4;
        border: 1px solid #33506E;
    }
</style>
"""


def apply():
    """Inject the SBI Hub global styles."""
    st.markdown(_CSS, unsafe_allow_html=True)
