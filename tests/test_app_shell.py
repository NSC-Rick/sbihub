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
    assert any("How can we help your client today?" in v for v in markdown_values)
    assert any("Better Insights. Better Decisions. Stronger Businesses." in v for v in markdown_values)
    assert any("Announcements & Updates" in v for v in markdown_values)


def test_landing_page_has_eight_module_cards(app):
    markdown_values = [m.value for m in app.markdown]
    cards = [v for v in markdown_values if 'class="sbi-card' in v]
    assert len(cards) == 8
    assert any("sbi-card-featured" in v for v in cards)


def test_financial_modeler_card_links_to_module(app):
    markdown_values = [m.value for m in app.markdown]
    assert any('href="?view=financial_modeler"' in v for v in markdown_values)


def test_sidebar_nav_links_render(app):
    markdown_values = [m.value for m in app.sidebar.markdown]
    for view in ("hub", "clients", "scenarios", "notes"):
        assert any(f'href="?view={view}"' in v for v in markdown_values)


def test_navigate_to_financial_modeler(app):
    app.session_state["active_view"] = "financial_modeler"
    app.run()

    assert not app.exception
    sidebar_titles = [t.value for t in app.sidebar.title] + [t.body for t in app.sidebar.title]
    assert any("Operating Model" in t for t in sidebar_titles)


def test_back_to_hub_navigation(app):
    app.session_state["active_view"] = "financial_modeler"
    app.run()
    assert not app.exception

    back_buttons = [b for b in app.sidebar.button if "Back to SBI Hub" in b.label]
    assert len(back_buttons) == 1
    back_buttons[0].click().run()

    assert not app.exception
    assert app.session_state["active_view"] == "hub"


def test_module_registry_module_names_on_cards(app):
    from sbi_hub.config.modules import MODULES
    markdown_values = [m.value for m in app.markdown]
    for module in MODULES:
        assert any(module["name"] in v for v in markdown_values), module["name"]
