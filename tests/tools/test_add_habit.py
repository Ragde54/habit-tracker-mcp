from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_habit import run


def test_add_habit_minimal(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    result = run({"name": "Morning run", "frequency_type": "daily"})
    assert "Morning run" in result[0].text


def test_add_habit_returns_id(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    result = run({"name": "Morning run", "frequency_type": "daily"})
    assert "id" in result[0].text


def test_add_habit_with_all_fields(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    result = run(
        {
            "name": "Read",
            "frequency_type": "weekly",
            "frequency_target": 3,
            "description": "Read for 30 minutes",
        }
    )
    assert "Read" in result[0].text


def test_add_habit_invalid_frequency_type(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({"name": "Run", "frequency_type": "hourly"})


def test_add_habit_missing_name(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({"frequency_type": "daily"})


def test_add_habit_frequency_target_zero(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({"name": "Run", "frequency_type": "daily", "frequency_target": 0})


def test_add_habit_with_valid_category(override_engine: Any) -> None:
    from habit_tracker_mcp.tools.add_category import run as add_category

    add_category({"name": "health"})
    result = run({"name": "Run", "frequency_type": "daily", "category_id": 1})
    assert "Run" in result[0].text


def test_add_habit_invalid_category_raises(override_engine: Any) -> None:
    with pytest.raises(ValueError, match="not found"):
        run({"name": "Run", "frequency_type": "daily", "category_id": 999})


def test_add_habit_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.add_habit.engine") as mock:
        mock.begin.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to add habit"):
            run({"name": "Run", "frequency_type": "daily"})
