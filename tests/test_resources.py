from typing import Any

from habit_tracker_mcp.resources import get_schema_contents


def test_schema_contains_all_tables(override_engine: Any) -> None:
    contents = get_schema_contents()
    assert "habits" in contents.text
    assert "todos" in contents.text
    assert "categories" in contents.text
    assert "habit_completions" in contents.text


def test_schema_contains_key_columns(override_engine: Any) -> None:
    contents = get_schema_contents()
    assert "frequency_type" in contents.text
    assert "archived_at" in contents.text
    assert "completed_at" in contents.text
    assert "sort_order" in contents.text


def test_schema_uri_correct(override_engine: Any) -> None:
    contents = get_schema_contents()
    assert str(contents.uri) == "db://schema"


def test_schema_mime_type(override_engine: Any) -> None:
    contents = get_schema_contents()
    assert contents.mimeType == "text/plain"


def test_schema_contains_foreign_keys(override_engine: Any) -> None:
    contents = get_schema_contents()
    assert "categories" in contents.text
    assert "habits" in contents.text
