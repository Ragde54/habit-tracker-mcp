from typing import Any

import pytest
from pydantic import ValidationError

from habit_tracker_mcp.tools.add_category import run


def test_add_category_minimal(override_engine: Any) -> None:
    result = run({"name": "health"})
    assert "health" in result[0].text


def test_add_category_with_color(override_engine: Any) -> None:
    result = run({"name": "health", "color": "#FF5733"})
    assert "health" in result[0].text


def test_add_category_invalid_color(override_engine: Any) -> None:
    with pytest.raises((ValidationError, ValueError)):
        run({"name": "health", "color": "red"})


def test_add_category_missing_name(override_engine: Any) -> None:
    with pytest.raises(ValidationError):
        run({})


def test_add_category_duplicate_name(override_engine: Any) -> None:
    run({"name": "health"})
    with pytest.raises(ValueError):
        run({"name": "health"})
