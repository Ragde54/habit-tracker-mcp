from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import AddHabitInput

tool_definition = Tool(
    name="add_habit",
    description=(
        "Use this tool when the user wants to start tracking a new habit. "
        "The tool will create the habit and return its ID, which can be used "
        "with other tools like 'link_habit_to_category'."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "frequency_type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
            "frequency_target": {"type": "integer", "default": 1},
            "description": {"type": "string"},
            "category_id": {"type": "integer"},
        },
        "required": ["name", "frequency_type"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Add a new habit."""
    params = AddHabitInput(**arguments)

    try:
        with engine.begin() as conn:
            if params.category_id is not None:
                category_exists = conn.execute(
                    text("SELECT 1 FROM categories WHERE id = :category_id"),
                    {"category_id": params.category_id},
                ).scalar()
                if not category_exists:
                    raise ValueError(f"Category '{params.category_id}' not found")

            result = conn.execute(
                text("""
                    INSERT INTO habits (name,
                                        description,
                                        category_id,
                                        frequency_type,
                                        frequency_target)
                    VALUES (:name,
                            :description,
                            :category_id,
                            :frequency_type,
                            :frequency_target)
                """),
                {
                    "name": params.name,
                    "description": params.description,
                    "category_id": params.category_id,
                    "frequency_type": params.frequency_type,
                    "frequency_target": params.frequency_target,
                },
            )
            return [
                TextContent(
                    type="text", text=f"Habit '{params.name}' added with id {result.lastrowid}"
                )
            ]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to add habit: {e}") from e
