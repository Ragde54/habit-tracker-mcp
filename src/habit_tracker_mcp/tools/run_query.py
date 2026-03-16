from typing import Any

from mcp.types import TextContent, Tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from habit_tracker_mcp.config import settings
from habit_tracker_mcp.database import engine
from habit_tracker_mcp.models.inputs import RunQueryInput
from habit_tracker_mcp.security import check_query_allowed

tool_definition = Tool(
    name="run_query",
    description=(
        "Execute a read-only SQL SELECT query against the habit tracker SQLite database. "
        "Use this for complex queries, aggregations, streak calculations, and anything "
        "not covered by the dedicated tools. "
        "Do NOT use this for writes — use add_habit, add_todo, complete_habit, "
        "complete_todo, and archive_habit instead. "
        "The db://schema resource contains the full table structure."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "The SQL query to execute"},
        },
        "required": ["sql"],
    },
)


def run(arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a read-only SQL query against the habit tracker database."""
    params = RunQueryInput(**arguments)
    check_query_allowed(params.sql, settings.read_only_mode)

    try:
        with engine.connect() as conn:
            result = conn.execute(text(params.sql))

            if result.returns_rows:
                columns = list(result.keys())
                rows = [list(row) for row in result.fetchall()]
                data = {"columns": columns, "rows": rows, "rowcount": len(rows)}
            else:
                conn.commit()
                data = {"columns": [], "rows": [], "rowcount": result.rowcount}

        return [TextContent(type="text", text=str(data))]

    except SQLAlchemyError as e:
        raise ValueError(f"Query failed: {e}") from e
