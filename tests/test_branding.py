"""Tests for the configurable branding system (sbi_hub/config/branding.py)."""
from pathlib import Path

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from sbi_hub.config import branding  # noqa: E402
from sbi_hub.modules.financial_modeler.utils import session_manager  # noqa: E402

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(session_manager, "SESSION_FILE", tmp_path / ".finlite_session.json")
    at = AppTest.from_file(str(APP_PATH))
    at.run()
    return at


def test_brand_config_complete():
    required = {
        "org_name", "org_subtitle", "product_name", "product_subtitle",
        "app_title", "page_icon", "tagline", "footer_icon",
        "logo_svg", "header_art_svg", "colors",
    }
    assert required <= set(branding.BRAND)


def test_brand_colors_complete():
    required = {
        "accent", "accent_dark", "accent_text", "accent_soft",
        "accent_soft_text", "accent_on_dark", "sidebar_bg", "sidebar_bg_deep",
    }
    assert required <= set(branding.BRAND["colors"])
    assert all(v.startswith("#") for v in branding.BRAND["colors"].values())


def test_default_brand_is_north_star(app):
    markdown_values = [m.value for m in app.sidebar.markdown]
    assert any("North Star Consulting" in v for v in markdown_values)
    assert any("Business Intelligence Platform" in v for v in markdown_values)


def test_no_legacy_org_branding(app):
    """No VtSBDC wording anywhere in the rendered chrome."""
    markdown_values = [m.value for m in app.markdown] + [
        m.value for m in app.sidebar.markdown
    ]
    blob = " ".join(markdown_values)
    assert "VtSBDC" not in blob
    assert "Vermont" not in blob


def test_product_identity_in_header(app):
    markdown_values = [m.value for m in app.markdown]
    assert any("Small Business Intelligence Hub" in v for v in markdown_values)
    assert any("Business Intelligence Workspace" in v for v in markdown_values)


def test_brand_css_tokens_substituted(app):
    """No %%TOKEN%% placeholders leak into the rendered CSS."""
    markdown_values = [m.value for m in app.markdown]
    assert not any("%%" in v for v in markdown_values)
    assert any(branding.BRAND["colors"]["accent"] in v for v in markdown_values)


def test_rebrand_requires_only_config_change(monkeypatch, tmp_path):
    """Patching BRAND values renames the org without touching components."""
    monkeypatch.setitem(branding.BRAND, "org_name", "Example Partner Org")
    monkeypatch.setattr(session_manager, "SESSION_FILE", tmp_path / ".finlite_session.json")
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    assert not at.exception
    markdown_values = [m.value for m in at.sidebar.markdown]
    assert any("Example Partner Org" in v for v in markdown_values)
