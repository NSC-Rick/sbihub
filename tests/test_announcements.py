"""Tests for the announcements config loader and ordering."""
import json

from sbi_hub.shell.announcements import load_announcements, sort_announcements


def _write(tmp_path, entries):
    path = tmp_path / "announcements.json"
    path.write_text(json.dumps(entries), encoding="utf-8")
    return path


def test_pinned_first_then_newest():
    entries = [
        {"title": "Old", "description": "d", "date": "2026-01-01", "category": "News", "pinned": True},
        {"title": "New", "description": "d", "date": "2026-11-01", "category": "News", "pinned": False},
        {"title": "Mid", "description": "d", "date": "2026-06-01", "category": "News", "pinned": False},
    ]
    ordered = sort_announcements(entries)
    assert [a["title"] for a in ordered] == ["Old", "New", "Mid"]


def test_loads_bundled_config():
    announcements = load_announcements()
    assert len(announcements) >= 1
    first = announcements[0]
    assert first.get("pinned") is True


def test_missing_file_returns_empty(tmp_path):
    assert load_announcements(tmp_path / "nope.json") == []


def test_malformed_json_returns_empty(tmp_path):
    path = tmp_path / "announcements.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_announcements(path) == []


def test_entries_missing_fields_skipped(tmp_path):
    path = _write(tmp_path, [
        {"title": "Complete", "description": "d", "date": "2026-11-01", "category": "News"},
        {"title": "No date", "description": "d", "category": "News"},
    ])
    loaded = load_announcements(path)
    assert [a["title"] for a in loaded] == ["Complete"]
