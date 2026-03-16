from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_habit import run as add_habit
from habit_tracker_mcp.tools.archive_habit import run as archive_habit


def test_archive_habit_success(override_engine: Any) -> None:
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    result = archive_habit({"habit_id": 1})
    assert "archived" in result[0].text.lower()


def test_archive_habit_not_found(override_engine: Any) -> None:
    with pytest.raises(ValueError, match="not found"):
        archive_habit({"habit_id": 999})


def test_archive_habit_already_archived(override_engine: Any) -> None:
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    archive_habit({"habit_id": 1})
    with pytest.raises(ValueError, match="already archived"):
        archive_habit({"habit_id": 1})


def test_archive_habit_sets_timestamp(override_engine: Any, db_session: Any) -> None:
    from sqlalchemy import text

    add_habit({"name": "Morning run", "frequency_type": "daily"})
    archive_habit({"habit_id": 1})
    row = db_session.execute(text("SELECT archived_at FROM habits WHERE id = 1")).fetchone()
    assert row.archived_at is not None


def test_archive_habit_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.archive_habit.engine") as mock:
        mock.begin.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to archive habit"):
            archive_habit({"habit_id": 1})
