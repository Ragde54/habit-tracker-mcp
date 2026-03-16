from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_habit import run as add_habit
from habit_tracker_mcp.tools.run_query import run as run_query


def test_run_query_select(override_engine: Any) -> None:
    result = run_query({"sql": "SELECT 1 as n"})
    assert "1" in result[0].text


def test_run_query_returns_columns_and_rows(override_engine: Any) -> None:
    add_habit({"name": "Morning run", "frequency_type": "daily"})
    result = run_query({"sql": "SELECT id, name FROM habits"})
    assert "Morning run" in result[0].text


def test_run_query_empty_result(override_engine: Any) -> None:
    result = run_query({"sql": "SELECT * FROM habits"})
    assert "rows" in result[0].text


def test_run_query_invalid_sql(override_engine: Any) -> None:
    with pytest.raises(ValueError, match="Query failed"):
        run_query({"sql": "SELECT * FROM nonexistent_table"})


def test_run_query_blocked_in_read_only_mode(override_engine: Any, monkeypatch: Any) -> None:
    import habit_tracker_mcp.tools.run_query as rq_mod
    from habit_tracker_mcp.config import Settings

    monkeypatch.setattr(rq_mod, "settings", Settings(read_only_mode=True))
    with pytest.raises(ValueError, match="read-only"):
        run_query({"sql": "INSERT INTO habits (name, frequency_type) VALUES ('x', 'daily')"})


def test_run_query_empty_sql_raises(override_engine: Any) -> None:
    with pytest.raises(Exception):
        run_query({"sql": ""})


def test_run_query_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.run_query.engine") as mock:
        mock.connect.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Query failed"):
            run_query({"sql": "SELECT 1"})
