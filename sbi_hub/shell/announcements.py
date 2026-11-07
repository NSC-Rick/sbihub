"""
Announcements & Updates panel.

Announcements are managed through ``sbi_hub/config/announcements.json``.
Each entry supports: title, description, date (ISO), category, and an
optional ``pinned`` flag. Entries render pinned-first, then newest-first.
"""
import html
import json
from datetime import date
from pathlib import Path

import streamlit as st

ANNOUNCEMENTS_FILE = Path(__file__).resolve().parent.parent / "config" / "announcements.json"

CATEGORY_COLORS = {
    "Release": "#2AA198",
    "Announcement": "#4C9F70",
    "Roadmap": "#7FA6C9",
    "Maintenance": "#C9A227",
    "News": "#8E7CC3",
}

REQUIRED_FIELDS = ("title", "description", "date", "category")


def load_announcements(path=None):
    """Load announcements from the JSON config file.

    Returns a list of announcement dicts sorted pinned-first, then
    newest-first. Malformed entries missing required fields are skipped.
    """
    path = Path(path) if path else ANNOUNCEMENTS_FILE
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    announcements = [a for a in data if isinstance(a, dict) and all(a.get(f) for f in REQUIRED_FIELDS)]
    return sort_announcements(announcements)


def sort_announcements(announcements):
    """Sort pinned announcements first, then by date descending."""
    def key(item):
        try:
            parsed = date.fromisoformat(str(item.get("date", "")))
        except ValueError:
            parsed = date.min
        return (0 if item.get("pinned") else 1, -parsed.toordinal())

    return sorted(announcements, key=key)


def _category_chip(category):
    color = CATEGORY_COLORS.get(category, "#5B7A99")
    return (
        f'<span style="background-color:{color}; color:#0E1C2B; '
        'font-size:0.72rem; font-weight:700; padding:2px 8px; '
        'border-radius:10px; letter-spacing:0.03em;">'
        f'{html.escape(str(category)).upper()}</span>'
    )


def render(limit=4):
    """Render the announcements panel on the landing page."""
    st.markdown("### 📣 Announcements & Updates")

    announcements = load_announcements()
    if not announcements:
        st.caption("No announcements at this time.")
        return

    for item in announcements[:limit]:
        pinned = "📌 " if item.get("pinned") else ""
        title = html.escape(str(item["title"]))
        description = html.escape(str(item["description"]))
        date_text = html.escape(str(item["date"]))
        st.markdown(
            f'<div class="sbi-announcement">'
            f'<div class="sbi-announcement-meta">{_category_chip(item["category"])}'
            f'<span class="sbi-announcement-date">{date_text}</span></div>'
            f'<div class="sbi-announcement-title">{pinned}{title}</div>'
            f'<div class="sbi-announcement-desc">{description}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
