from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.tools.add_category import run as add_category
from habit_tracker_mcp.tools.list_categories import run as list_categories


def test_list_categories_empty(override_engine: Any) -> None:
    result = list_categories({})
    assert "No categories" in result[0].text


def test_list_categories_returns_all(override_engine: Any) -> None:
    add_category({"name": "health", "color": "#FF5733"})
    add_category({"name": "learning", "color": "#33C1FF"})
    result = list_categories({})
    assert "health" in result[0].text
    assert "learning" in result[0].text


def test_list_categories_shows_color(override_engine: Any) -> None:
    add_category({"name": "health", "color": "#FF5733"})
    result = list_categories({})
    assert "#FF5733" in result[0].text


def test_list_categories_db_failure(override_engine: Any) -> None:
    with patch("habit_tracker_mcp.tools.list_categories.engine") as mock:
        mock.connect.side_effect = SQLAlchemyError("connection lost")
        with pytest.raises(ValueError, match="Failed to list categories"):
            list_categories({})
