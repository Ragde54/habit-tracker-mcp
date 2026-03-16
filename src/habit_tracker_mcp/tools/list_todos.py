from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import ListTodosInput

tool_definition = Tool(
    name="list_todos",
    description=(
        "List all todos with their IDs, due dates, and completion status. "
        "Call this before completing, archiving, or linking a todo "
        "to find a valid todo_id."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "category_id": {"type": "integer", "description": "Filter by category"},
            "habit_id": {"type": "integer", "description": "Filter by habit"},
            "completed": {"type": "boolean", "description": "Filter by completion status"},
        },
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """List todos with optional filters."""
    params = ListTodosInput(**arguments)

    conditions = []
    bind_params: dict[str, Any] = {}

    if params.completed is True:
        conditions.append("completed_at IS NOT NULL")
    elif params.completed is False:
        conditions.append("completed_at IS NULL")

    if params.category_id is not None:
        conditions.append("category_id = :category_id")
        bind_params["category_id"] = params.category_id

    if params.habit_id is not None:
        conditions.append("habit_id = :habit_id")
        bind_params["habit_id"] = params.habit_id

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT id, title, notes, due_date, completed_at FROM todos {where_clause}"),
                bind_params,
            )
            todos = result.fetchall()

            if not todos:
                return [TextContent(type="text", text="No todos found.")]

            lines = []
            for todo in todos:
                status = " [completed]" if todo.completed_at else ""
                due_date_str = f" | due={todo.due_date}" if todo.due_date else ""
                lines.append(
                    f"- id={todo.id} | {todo.title}{status}{due_date_str} | "
                    f"{todo.notes or 'no notes'}"
                )

            return [TextContent(type="text", text="\n".join(lines))]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to list todos: {e}") from e
