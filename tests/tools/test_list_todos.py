from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_todo import run as add_todo
from habit_tracker_mcp.tools.complete_todo import run as complete_todo
from habit_tracker_mcp.tools.list_todos import run as list_todos


def test_list_todos_empty(override_engine: Any) -> None:
    result = list_todos({})
    assert "No todos" in result[0].text


def test_list_todos_returns_all(override_engine: Any) -> None:
    add_todo({"title": "Buy groceries"})
    add_todo({"title": "Call dentist"})
    result = list_todos({})
    assert "Buy groceries" in result[0].text
    assert "Call dentist" in result[0].text


def test_list_todos_filter_incomplete(override_engine: Any) -> None:
    add_todo({"title": "Buy groceries"})
    add_todo({"title": "Call dentist"})
    complete_todo({"todo_id": 1})
    result = list_todos({"completed": False})
    assert "Call dentist" in result[0].text
    assert "Buy groceries" not in result[0].text


def test_list_todos_filter_completed(override_engine: Any) -> None:
    add_todo({"title": "Buy groceries"})
    complete_todo({"todo_id": 1})
    result = list_todos({"completed": True})
    assert "Buy groceries" in result[0].text


def test_list_todos_filter_by_category(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "work"})
    add_todo({"title": "Write report", "category_id": 1})
    add_todo({"title": "Buy groceries"})
    result = list_todos({"category_id": 1})
    assert "Write report" in result[0].text
    assert "Buy groceries" not in result[0].text


def test_list_todos_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.list_todos.engine") as mock:
        mock.connect.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to list todos"):
            list_todos({})
