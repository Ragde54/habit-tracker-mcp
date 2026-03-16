from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_habit import run as add_habit
from habit_tracker_mcp.tools.complete_habit import run as complete_habit


def test_complete_habit_success(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    result = complete_habit({"habit_id": 1})
    assert "completion" in result[0].text.lower()


def test_complete_habit_returns_id(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    result = complete_habit({"habit_id": 1})
    assert "id" in result[0].text


def test_complete_habit_with_note(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    result = complete_habit({"habit_id": 1, "note": "felt great"})
    assert "completion" in result[0].text.lower()


def test_complete_habit_not_found(override_engine: Any) -> None:
    with pytest.raises(ValueError, match="not found"):
        complete_habit({"habit_id": 999})


def test_complete_habit_invalid_date(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    with pytest.raises(ValidationError):
        complete_habit({"habit_id": 1, "completed_at": "not-a-date"})


def test_complete_habit_source_is_manual(override_engine: Any, db_session: Any) -> None:
    from sqlalchemy import text

    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    complete_habit({"habit_id": 1})
    row = db_session.execute(
        text("SELECT source FROM habit_completions WHERE habit_id = 1")
    ).fetchone()
    assert row is not None
    assert row.source == "manual"


def test_complete_habit_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.complete_habit.engine") as mock:
        mock.begin.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to log habit completion"):
            complete_habit({"habit_id": 1})
