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
    assert sum("sbi-card-soon" in v for v in cards) == 7


def test_financial_modeler_card_launches_new_tab(app):
    """The featured card links to the standalone app path in a new tab."""
    markdown_values = [m.value for m in app.markdown]
    assert any('href="/fm" target="_blank"' in v for v in markdown_values)
    assert any("Opens in a new tab" in v for v in markdown_values)


def test_no_embedded_open_buttons_on_landing(app):
    """No module currently embeds in the hub shell — no open buttons."""
    assert not [b for b in app.button if b.key.startswith("open_")]


def test_sidebar_nav_buttons_render(app):
    keys = [b.key for b in app.sidebar.button]
    for view in ("hub", "clients", "scenarios", "notes"):
        assert f"nav_{view}" in keys


def test_sidebar_nav_button_switches_view(app):
    app.sidebar.button(key="nav_scenarios").click().run()

    assert not app.exception
    assert app.session_state["active_view"] == "scenarios"
    markdown_values = [m.value for m in app.markdown]
    assert any("Saved Scenarios" in v for v in markdown_values)


def test_query_param_view_deep_link(app):
    app.query_params["view"] = "clients"
    app.run()

    assert not app.exception
    assert app.session_state["active_view"] == "clients"
    assert "view" not in app.query_params


def test_query_param_invalid_view_ignored(app):
    app.query_params["view"] = "not_a_real_view"
    app.run()

    assert not app.exception
    assert app.session_state["active_view"] == "hub"


def test_financial_modeler_view_shows_launcher(app):
    """?view=financial_modeler renders a launcher, not the embedded app."""
    app.session_state["active_view"] = "financial_modeler"
    app.run()

    assert not app.exception
    markdown_values = [m.value for m in app.markdown]
    assert any('href="/fm" target="_blank"' in v for v in markdown_values)
    assert any("Open Financial Modeler in a new tab" in v for v in markdown_values)
    # The hub chrome is present; the modeler itself is not embedded.
    assert not any("Operating Model" in t.value for t in app.sidebar.title)


def test_back_to_hub_navigation(app):
    app.session_state["active_view"] = "automation_ai"
    app.run()
    assert not app.exception

    back_buttons = [b for b in app.sidebar.button if "Back to SBI Hub" in b.label]
    assert len(back_buttons) == 1
    back_buttons[0].click().run()

    assert not app.exception
    assert app.session_state["active_view"] == "hub"


def test_coming_soon_module_renders_placeholder(app):
    app.session_state["active_view"] = "automation_ai"
    app.run()

    assert not app.exception
    markdown_values = [m.value for m in app.markdown]
    assert any("Automation & AI Opportunity Evaluator" in v for v in markdown_values)
    back_buttons = [b for b in app.sidebar.button if "Back to SBI Hub" in b.label]
    assert len(back_buttons) == 1


def test_state_preserved_across_navigation(app):
    """Session state must survive hub-view round-trips (no page reloads)."""
    app.sidebar.button(key="nav_clients").click().run()
    assert app.session_state["active_view"] == "clients"

    app.session_state["sentinel"] = "still-here"
    app.sidebar.button(key="nav_hub").click().run()
    assert app.session_state["active_view"] == "hub"
    assert app.session_state["sentinel"] == "still-here"

    app.sidebar.button(key="nav_notes").click().run()
    assert app.session_state["active_view"] == "notes"
    assert app.session_state["sentinel"] == "still-here"


def test_module_registry_module_names_on_cards(app):
    from sbi_hub.config.modules import MODULES
    markdown_values = [m.value for m in app.markdown]
    for module in MODULES:
        assert any(module["name"] in v for v in markdown_values), module["name"]
