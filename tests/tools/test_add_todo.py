from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_todo import run


def test_add_todo_minimal(override_engine: Any) -> None:
    result = run({"title": "Buy groceries"})
    assert "Buy groceries" in result[0].text


def test_add_todo_returns_id(override_engine: Any) -> None:
    result = run({"title": "Buy groceries"})
    assert "id" in result[0].text


def test_add_todo_with_all_fields(override_engine: Any) -> None:
    result = run(
        {
            "title": "Buy groceries",
            "notes": "Remember milk",
            "priority": "high",
            "due_date": "2026-12-31",
        }
    )
    assert "Buy groceries" in result[0].text


def test_add_todo_invalid_priority(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({"title": "Buy groceries", "priority": "urgent"})


def test_add_todo_missing_title(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({})


def test_add_todo_invalid_due_date(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({"title": "Buy groceries", "due_date": "not-a-date"})


def test_add_todo_with_habit_link(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_habit import run as add_habit

    add_habit({"name": "Exercise", "frequency_type": "daily"})
    result = run({"title": "Go for a run", "habit_id": 1})
    assert "Go for a run" in result[0].text


def test_add_todo_invalid_habit_link(override_engine: Any) -> None:
    with pytest.raises(ValueError, match="not found"):
        run({"title": "Go for a run", "habit_id": 999})


def test_add_todo_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.add_todo.engine") as mock:
        mock.begin.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to add todo"):
            run({"title": "Buy groceries"})
