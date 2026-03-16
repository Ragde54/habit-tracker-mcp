from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import ListCategoriesInput

tool_definition = Tool(
    name="list_categories",
    description=(
        "List all available categories with their IDs, colors, and sort order. "
        "Call this before creating a habit or todo to find a valid category_id, "
        "or to show the user what categories exist."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """List all categories."""
    ListCategoriesInput(**arguments)

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, color, sort_order FROM categories ORDER BY sort_order")
            )
            categories = result.fetchall()

            if not categories:
                return [TextContent(type="text", text="No categories found.")]

            lines = []
            for category in categories:
                color = f" | {category.color}" if category.color else ""
                lines.append(
                    f"- id={category.id} | {category.name}{color} | order={category.sort_order}"
                )  # noqa: E501

            return [TextContent(type="text", text="\n".join(lines))]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to list categories: {e}") from e
