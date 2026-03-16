from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_habit import run as add_habit
from habit_tracker_mcp.tools.add_todo import run as add_todo
from habit_tracker_mcp.tools.complete_todo import run as complete_todo


def test_complete_todo_no_habit_link(override_engine: Any) -> None:
    add_todo({"title": "Buy groceries"})
    result = complete_todo({"todo_id": 1})
    assert "complete" in result[0].text.lower()


def test_complete_todo_with_habit_link(override_engine: Any) -> None:
    add_habit({"name": "Exercise", "frequency_type": "daily"})
    add_todo({"title": "Go for a run", "habit_id": 1})
    result = complete_todo({"todo_id": 1})
    assert "habit_completion" in result[0].text


def test_complete_todo_already_completed(override_engine: Any) -> None:
    add_todo({"title": "Buy groceries"})
    complete_todo({"todo_id": 1})
    with pytest.raises(ValueError, match="already completed"):
        complete_todo({"todo_id": 1})


def test_complete_todo_not_found(override_engine: Any) -> None:
    with pytest.raises(ValueError, match="not found"):
        complete_todo({"todo_id": 999})


def test_complete_todo_auto_logs_source_todo(override_engine: Any, db_session: Any) -> None:
    from sqlalchemy import text

    add_habit({"name": "Exercise", "frequency_type": "daily"})
    add_todo({"title": "Go for a run", "habit_id": 1})
    complete_todo({"todo_id": 1})
    row = db_session.execute(
        text("SELECT source FROM habit_completions WHERE habit_id = 1")
    ).fetchone()
    assert row.source == "todo"


def test_complete_todo_without_habit_link_no_completion_logged(
    override_engine: Any, db_session: Any
) -> None:
    from sqlalchemy import text

    add_todo({"title": "Buy groceries"})
    complete_todo({"todo_id": 1})
    row = db_session.execute(text("SELECT COUNT(*) as count FROM habit_completions")).fetchone()
    assert row.count == 0


def test_complete_todo_atomic_both_or_neither(override_engine: Any, db_session: Any) -> None:
    from unittest.mock import patch

    from sqlalchemy import text

    add_habit({"name": "Exercise", "frequency_type": "daily"})
    add_todo({"title": "Go for a run", "habit_id": 1})
    with patch("habit_tracker_mcp.tools.complete_todo.engine") as mock_engine:
        mock_engine.begin.side_effect = Exception("DB failure")
        with pytest.raises(Exception):
            complete_todo({"todo_id": 1})
    todo_row = db_session.execute(text("SELECT completed_at FROM todos WHERE id = 1")).fetchone()
    completion_row = db_session.execute(
        text("SELECT COUNT(*) as count FROM habit_completions")
    ).fetchone()
    assert todo_row.completed_at is None
    assert completion_row.count == 0


def test_complete_todo_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.complete_todo.engine") as mock:
        mock.begin.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to complete todo"):
            complete_todo({"todo_id": 1})
