from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_habit import run as add_habit
from habit_tracker_mcp.tools.archive_habit import run as archive_habit
from habit_tracker_mcp.tools.list_habits import run as list_habits


def test_list_habits_empty(override_engine: Any) -> None:
    result = list_habits({})
    assert "No habits" in result[0].text


def test_list_habits_returns_active(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    result = list_habits({})
    assert "Morning run" in result[0].text


def test_list_habits_excludes_archived_by_default(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    archive_habit({"habit_id": 1})
    result = list_habits({})
    assert "No habits" in result[0].text


def test_list_habits_includes_archived_when_requested(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    archive_habit({"habit_id": 1})
    result = list_habits({"include_archived": True})
    assert "Morning run" in result[0].text


def test_list_habits_filter_by_category(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    add_category({"name": "learning"})
    add_habit({"name": "Run", "frequency_type": "daily", "category_id": 1})
    add_habit({"name": "Read", "frequency_type": "daily", "category_id": 2})
    result = list_habits({"category_id": 1})
    assert "Run" in result[0].text
    assert "Read" not in result[0].text


def test_list_habits_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.list_habits.engine") as mock:
        mock.connect.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to list habits"):
            list_habits({})
