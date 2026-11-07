"""App-level tests for the SBI Hub shell using Streamlit's AppTest."""
from pathlib import Path

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from sbi_hub.modules.financial_modeler.utils import session_manager  # noqa: E402

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


@pytest.fixture
def app(monkeypatch, tmp_path):
    """Run the app with session persistence redirected to a temp file."""
    monkeypatch.setattr(session_manager, "SESSION_FILE", tmp_path / ".finlite_session.json")
    at = AppTest.from_file(str(APP_PATH))
    at.run()
    return at


def test_landing_page_renders(app):
    assert not app.exception

    markdown_values = [m.value for m in app.markdown]
    assert any("Welcome to SBI Hub" in v for v in markdown_values)
    assert any("Better Insights. Better Decisions. Stronger Businesses." in v for v in markdown_values)
    assert any("Announcements & Updates" in v for v in markdown_values)


def test_landing_page_has_eight_module_buttons(app):
    labels = [b.label for b in app.button]
    assert "Open Financial Modeler" in labels
    assert labels.count("Coming Soon") == 7


def test_navigate_to_financial_modeler(app):
    app.button(key="open_financial_modeler").click().run()

    assert not app.exception
    assert app.session_state["active_view"] == "financial_modeler"
    sidebar_titles = [t.value for t in app.sidebar.title] + [t.body for t in app.sidebar.title]
    assert any("Operating Model" in t for t in sidebar_titles)


def test_back_to_hub_navigation(app):
    app.button(key="open_financial_modeler").click().run()
    assert not app.exception

    back_buttons = [b for b in app.sidebar.button if "Back to SBI Hub" in b.label]
    assert len(back_buttons) == 1
    back_buttons[0].click().run()

    assert not app.exception
    assert app.session_state["active_view"] == "hub"
