from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)

from habit_tracker_mcp.resources import get_schema_contents

SQL_ASSISTANT_PROMPT = Prompt(
    name="sql-assistant",
    description=(
        "Sets up client as a SQL assistant with full knowledge of the "
        "habit tracker schema. Use this before writing any queries."
    ),
    arguments=[
        PromptArgument(
            name="focus",
            description="Optional area to focus on, e.g. 'habits', 'todos', 'streaks'",
            required=False,
        )
    ],
)


def get_sql_assistant(focus: str | None = None) -> GetPromptResult:
    """Build the SQL assistant prompt with live schema injected."""
    schema = get_schema_contents().text
    focus_instruction = (
        f"\nFocus particularly on the '{focus}' area for this session." if focus else ""
    )

    system_message = f"""You are a SQL assistant for a habit tracker application using SQLite.

You have access to the run_query tool to execute SELECT queries against the database.
You also have access to dedicated tools for writes: add_habit, add_todo, complete_habit,
complete_todo, add_category, list_categories, list_habits, list_todos, and archive_habit.
Always use the dedicated write tools instead of raw SQL for any mutations.

{schema}

Guidelines:
- Always use parameterized queries mentally — the run_query tool handles this for you
- For streak calculations, use SQLite date functions: date(), strftime(), julianday()
- habits.archived_at IS NULL means the habit is active
- todos.completed_at IS NULL means the todo is incomplete
- habit_completions.source = 'todo' means the completion was auto-logged{focus_instruction}
"""

    return GetPromptResult(
        description="SQL assistant with live habit tracker schema",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=system_message),
            )
        ],
    )
