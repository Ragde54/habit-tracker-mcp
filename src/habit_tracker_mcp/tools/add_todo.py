from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import AddTodoInput

tool_definition = Tool(
    name="add_todo",
    description=(
        "Use this tool when the user wants to add a new todo item. "
        "The tool will create the todo and return its ID, which can be used "
        "with other tools like 'link_todo_to_category'."
        "Call list_categories first if you want to assign a category to the todo."
        "Call list_habits first if you want to assign a habit to the todo."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "notes": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "due_date": {"type": "string", "description": "ISO 8601 date string"},
            "category_id": {"type": "integer"},
            "habit_id": {"type": "integer"},
        },
        "required": ["title"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Add a new todo to the tracker."""
    params = AddTodoInput(**arguments)

    try:
        with engine.begin() as conn:
            if params.category_id is not None:
                category_exists = conn.execute(
                    text("SELECT 1 FROM categories WHERE id = :category_id"),
                    {"category_id": params.category_id},
                ).scalar()
                if not category_exists:
                    raise ValueError(f"Category '{params.category_id}' not found")

            if params.habit_id is not None:
                habit_exists = conn.execute(
                    text("SELECT 1 FROM habits WHERE id = :habit_id AND archived_at IS NULL"),
                    {"habit_id": params.habit_id},
                ).scalar()
                if not habit_exists:
                    raise ValueError(f"Habit '{params.habit_id}' not found")

            result = conn.execute(
                text("""
                    INSERT INTO todos (title, notes, priority, due_date, category_id, habit_id)
                    VALUES (:title, :notes, :priority, :due_date, :category_id, :habit_id)
                """),
                {
                    "title": params.title,
                    "notes": params.notes,
                    "priority": params.priority,
                    "due_date": params.due_date,
                    "category_id": params.category_id,
                    "habit_id": params.habit_id,
                },
            )
            return [
                TextContent(
                    type="text", text=f"Todo '{params.title}' added with id {result.lastrowid}"
                )
            ]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to add todo: {e}") from e
