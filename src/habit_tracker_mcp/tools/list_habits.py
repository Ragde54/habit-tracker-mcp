from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import ListHabitsInput

tool_definition = Tool(
    name="list_habits",
    description=(
        "List habits with their IDs, frequency, and status. "
        "Call this before completing, archiving, or linking a habit "
        "to find a valid habit_id."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "category_id": {"type": "integer", "description": "Filter by category"},
            "include_archived": {
                "type": "boolean",
                "description": "Include archived habits",
                "default": False,
            },
        },
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """List habits with optional filters."""
    params = ListHabitsInput(**arguments)

    conditions = []
    bind_params: dict[str, Any] = {}

    if not params.include_archived:
        conditions.append("archived_at IS NULL")

    if params.category_id is not None:
        conditions.append("category_id = :category_id")
        bind_params["category_id"] = params.category_id

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"SELECT id, name, description, frequency_type, \
                    frequency_target, archived_at FROM habits {where_clause}"
                ),
                bind_params,
            )
            habits = result.fetchall()

            if not habits:
                return [TextContent(type="text", text="No habits found.")]

            lines = []
            for habit in habits:
                status = " [archived]" if habit.archived_at else ""
                lines.append(
                    f"- id={habit.id} | {habit.name}{status} | "
                    f"{habit.frequency_target}x {habit.frequency_type} | "
                    f"{habit.description or 'no description'}"
                )

            return [TextContent(type="text", text="\n".join(lines))]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to list habits: {e}") from e
