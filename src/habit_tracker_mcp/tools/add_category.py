from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import AddCategoryInput

tool_definition = Tool(
    name="add_category",
    description=(
        "Use this tool when the user wants to create a new category. "
        "The tool will create the category and return its ID, which can be used "
        "with other tools like 'add_habit' or 'add_todo'."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "color": {"type": "string"},
            "sort_order": {"type": "integer"},
        },
        "required": ["name"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Add a new category."""
    params = AddCategoryInput(**arguments)

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                INSERT INTO categories (name, color, sort_order)
                VALUES (:name, :color, :sort_order)
            """),
                {
                    "name": params.name,
                    "color": params.color,
                    "sort_order": params.sort_order,
                },
            )
            return [
                TextContent(
                    type="text", text=f"Category '{params.name}' added with id {result.lastrowid}"
                )
            ]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to add category: {e}") from e
