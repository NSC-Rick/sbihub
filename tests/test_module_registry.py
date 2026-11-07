"""Tests for the SBI Hub module registry."""
from sbi_hub.config.modules import MODULES, STATUS_ACTIVE, STATUS_COMING_SOON, get_module


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
