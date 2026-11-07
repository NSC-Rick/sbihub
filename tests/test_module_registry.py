"""Tests for the SBI Hub module registry."""
from sbi_hub.config.modules import (
    MODULES,
    STATUS_ACTIVE,
    STATUS_COMING_SOON,
    get_module,
    resolve_entry_point,
)
from sbi_hub.shell.icons import icon


def test_eight_modules_registered():
    assert len(MODULES) == 8


def test_module_ids_unique():
    ids = [m["id"] for m in MODULES]
    assert len(ids) == len(set(ids))


def test_required_fields_present():
    required = {"id", "name", "icon", "tagline", "description", "status"}
    for module in MODULES:
        assert required <= set(module), f"{module['id']} missing fields"


def test_exactly_one_active_module():
    active = [m for m in MODULES if m["status"] == STATUS_ACTIVE]
    assert [m["id"] for m in active] == ["financial_modeler"]


def test_remaining_modules_coming_soon():
    soon = [m for m in MODULES if m["status"] != STATUS_ACTIVE]
    assert len(soon) == 7
    assert all(m["status"] == STATUS_COMING_SOON for m in soon)


def test_get_module_lookup():
    assert get_module("financial_modeler")["name"] == "Financial Modeler"
    assert get_module("does_not_exist") is None


def test_approved_module_ids_present():
    ids = {m["id"] for m in MODULES}
    assert "automation_ai" in ids
    assert "idea_feasibility" in ids
    assert "idea_evaluator" not in ids
    assert "startup_feasibility" not in ids


def test_icon_keys_resolve():
    for module in MODULES:
        assert "<svg" in icon(module["icon"]), f"{module['id']} icon missing"


def test_active_modules_have_one_launch_mechanism():
    for module in MODULES:
        if module["status"] == STATUS_ACTIVE:
            has_entry = bool(module.get("entry_point"))
            has_url = bool(module.get("launch_url"))
            assert has_entry != has_url, (
                f"{module['id']} needs exactly one of entry_point/launch_url"
            )
            if has_entry:
                assert callable(resolve_entry_point(module))


def test_financial_modeler_launches_standalone_app():
    module = get_module("financial_modeler")
    assert module["launch_url"] == "/fm"
