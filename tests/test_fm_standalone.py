"""Tests for the standalone Financial Modeler entry point (fm_app.py)."""
from pathlib import Path

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from sbi_hub.modules.financial_modeler.utils import session_manager  # noqa: E402

APP_PATH = Path(__file__).resolve().parent.parent / "fm_app.py"


@pytest.fixture
def app(monkeypatch, tmp_path):
    """Run the standalone FM app with session persistence redirected."""
    monkeypatch.setattr(session_manager, "SESSION_FILE", tmp_path / ".finlite_session.json")
    at = AppTest.from_file(str(APP_PATH))
    at.run()
    return at


def test_standalone_fm_renders(app):
    assert not app.exception
    sidebar_titles = [t.value for t in app.sidebar.title]
    assert any("Financial Modeler" in t for t in sidebar_titles)


def test_standalone_fm_has_no_hub_chrome(app):
    """No SBI Hub sidebar branding or header bar inside the modeler."""
    markdown_values = [m.value for m in app.markdown] + [
        m.value for m in app.sidebar.markdown
    ]
    assert not any("sbi-logo-title" in v for v in markdown_values)
    assert not any("sbi-header" in v for v in markdown_values)
    # The hub light-theme flag is not set in the standalone app.
    assert "sbi_theme" not in app.session_state


def test_standalone_fm_navigation_preserved(app):
    """The original 'Go to' page radio exists with all nine screens."""
    radios = app.sidebar.radio
    assert len(radios) >= 1
    options = radios[0].options
    assert len(options) == 9


def test_serve_routing():
    """serve.py sends /fm to the modeler process and everything else to the hub."""
    import serve

    assert serve.is_fm_path("/fm")
    assert serve.is_fm_path("/fm/")
    assert serve.is_fm_path("/fm/_stcore/stream")
    assert not serve.is_fm_path("/")
    assert not serve.is_fm_path("/fmabc")
    assert serve.upstream_for("/fm").endswith(str(serve.FM_PORT))
    assert serve.upstream_for("/x").endswith(str(serve.HUB_PORT))
