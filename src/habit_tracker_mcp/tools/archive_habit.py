from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import ArchiveHabitInput

tool_definition = Tool(
    name="archive_habit",
    description=(
        "Use this tool when the user wants to stop tracking a habit but keep its history. "
        "The tool will soft-delete the habit by setting its archived_at timestamp."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "habit_id": {"type": "integer"},
            "archived_at": {"type": "string", "description": "ISO 8601 datetime string"},
        },
        "required": ["habit_id"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Soft-delete a habit by setting its archived_at timestamp."""
    params = ArchiveHabitInput(**arguments)

    try:
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT id, archived_at FROM habits WHERE id = :id"),
                {"id": params.habit_id},
            ).fetchone()

            if row is None:
                raise ValueError(f"Habit {params.habit_id} not found")

            if row.archived_at is not None:
                raise ValueError(f"Habit {params.habit_id} is already archived")

            conn.execute(
                text("UPDATE habits SET archived_at = :archived_at WHERE id = :id"),
                {"archived_at": params.archived_at, "id": params.habit_id},
            )

        return [
            TextContent(
                type="text",
                text=str(
                    {
                        "success": True,
                        "habit_id": params.habit_id,
                        "archived_at": params.archived_at,
                        "message": f"Habit {params.habit_id} archived successfully",
                    }
                ),
            )
        ]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to archive habit: {e}") from e
