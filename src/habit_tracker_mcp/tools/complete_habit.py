from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import CompleteHabitInput

tool_definition = Tool(
    name="complete_habit",
    description=(
        "Log a completion for a habit. Habits can be completed multiple times — "
        "once per period based on their frequency_type. Check existing completions "
        "with run_query before logging to avoid duplicates."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "habit_id": {"type": "integer"},
            "note": {"type": "string"},
            "completed_at": {"type": "string", "description": "ISO 8601 datetime string"},
        },
        "required": ["habit_id"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Log a completion for a habit."""
    params = CompleteHabitInput(**arguments)

    try:
        with engine.begin() as conn:
            habit_exists = conn.execute(
                text("SELECT 1 FROM habits WHERE id = :habit_id"),
                {"habit_id": params.habit_id},
            ).scalar()

            if not habit_exists:
                raise ValueError(f"Habit '{params.habit_id}' not found")

            result = conn.execute(
                text("""
                    INSERT INTO habit_completions (habit_id, completed_at, note, source)
                    VALUES (:habit_id, :completed_at, :note, :source)
                """),
                {
                    "habit_id": params.habit_id,
                    "completed_at": params.completed_at,
                    "note": params.note,
                    "source": "manual",
                },
            )
            return [
                TextContent(
                    type="text",
                    text=f"Habit completion logged successfully with id {result.lastrowid}",
                )
            ]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to log habit completion: {e}") from e
