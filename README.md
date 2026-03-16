# habit-tracker-mcp

A production-grade MCP server for tracking habits and todos, backed by SQLite. Implements all three MCP primitives: Tools, Resources, and Prompts.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose
- Node.js (for the MCP inspector)

## Local setup
```bash
make install
cp .env.example .env
make migrate
make run
```

## Docker setup
```bash
make docker-build
make docker-run
```

## Tools

| Tool | Required params | Description |
|---|---|---|
| `run_query` | `sql` | Execute a read-only SELECT query |
| `add_habit` | `name`, `frequency_type` | Create a new habit |
| `list_habits` | — | List active habits |
| `complete_habit` | `habit_id` | Log a habit completion |
| `archive_habit` | `habit_id` | Soft-delete a habit |
| `add_todo` | `title` | Create a new todo |
| `list_todos` | — | List todos with optional filters |
| `complete_todo` | `todo_id` | Mark a todo complete, auto-logs habit completion if linked |
| `add_category` | `name` | Create a category |
| `list_categories` | — | List all categories |

## Tool access policy

The AI has no delete capabilities by design. Destructive operations
(delete habit, delete category, delete todo) are intentionally omitted
from the MCP tool set and reserved for direct database access or a
future frontend interface.

To permanently remove data, connect directly to the database:
sqlite3 habit_tracker.db

## Resources

| URI | Description |
|---|---|
| `db://schema` | Live database schema with tables, columns, foreign keys and indexes |

## Prompts

| Name | Description |
|---|---|
| `sql-assistant` | Sets up client with full schema knowledge before writing queries |

## ⚠️ Warnings

- `docker-compose down -v` permanently destroys the database volume and all data
- `READ_ONLY_MODE=true` in `.env` blocks all write operations
- Never run `DROP TABLE` through `run_query` — there is no undo
