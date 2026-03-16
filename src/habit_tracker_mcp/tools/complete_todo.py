from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import CompleteTodoInput

tool_definition = Tool(
    name="complete_todo",
    description=(
        "Use this tool when the user wants to mark a todo as complete. "
        "The tool will create a completion record and return its ID. "
        "If the todo is linked to a habit, the tool will also log a habit completion."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "todo_id": {"type": "integer"},
            "note": {"type": "string"},
            "completed_at": {"type": "string", "description": "ISO 8601 datetime string"},
        },
        "required": ["todo_id"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Mark a todo as complete. If the todo is linked to a habit, also logs a habit completion."""
    params = CompleteTodoInput(**arguments)

    try:
        with engine.begin() as conn:
            # Step 1: fetch the todo
            row = conn.execute(
                text("SELECT id, habit_id, completed_at FROM todos WHERE id = :id"),
                {"id": params.todo_id},
            ).fetchone()

            if row is None:
                raise ValueError(f"Todo {params.todo_id} not found")

            if row.completed_at is not None:
                raise ValueError(f"Todo {params.todo_id} is already completed")

            # Step 2: mark the todo complete
            conn.execute(
                text("UPDATE todos SET completed_at = :completed_at WHERE id = :id"),
                {"completed_at": params.completed_at, "id": params.todo_id},
            )

            # Step 3: auto-log habit completion if linked
            completion_id = None
            if row.habit_id is not None:
                result = conn.execute(
                    text("""
                        INSERT INTO habit_completions (habit_id, completed_at, note, source)
                        VALUES (:habit_id, :completed_at, :note, :source)
                    """),
                    {
                        "habit_id": row.habit_id,
                        "completed_at": params.completed_at,
                        "note": params.note,
                        "source": "todo",
                    },
                )
                completion_id = result.lastrowid

        response: dict[str, Any] = {
            "success": True,
            "todo_id": params.todo_id,
            "message": "Todo marked as complete",
        }
        if completion_id is not None:
            response["habit_completion_id"] = completion_id
            response["message"] += " and habit completion logged"

        return [TextContent(type="text", text=str(response))]

    except SQLAlchemyError as e:
        raise ValueError(f"Failed to complete todo: {e}") from e
