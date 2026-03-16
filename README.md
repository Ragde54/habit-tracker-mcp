# habit-tracker-mcp

A production-grade Model Context Protocol (MCP) server for tracking personal habits and todos. It provides a robust bridge between Large Language Models (LLMs) and a persistent SQLite backend, enabling AI assistants to help you maintain consistency and analyze your productivity patterns.

## 🚀 Key Features

- **Habit Tracking**: Manage recurring habits with flexible frequency targets.
- **Todo Management**: Track one-off tasks with priorities and due dates.
- **Linked Automation**: Cross-linking allows todos to automatically log habit completions upon fulfillment.
- **Categorization**: Shared category system for unified organization.
- **AI-Powered Analysis**: Specialized `sql-assistant` prompt and live schema resources for deep data introspection.

## 🛠 Design Decisions

- **Safety-First Writes**: Mutations are restricted to specific high-level tools; the raw SQL tool is strictly read-only (`SELECT` only).
- **Preservation by Default**: Implements soft-deletion (archiving) instead of permanent removal to protect user history.
- **Modern Stack**: Built with Python 3.12, SQLAlchemy 2.0, Pydantic, and `uv` for lightning-fast dependency management.
- **Ready for Production**: Includes full Docker integration, automated migrations with Alembic, and a 95%+ coverage test suite.

## 📂 Project Structure

```text
.
├── alembic/              # Database migration history
├── docker/               # Containerization (Dockerfile, Compose)
├── src/
│   └── habit_tracker_mcp/
│       ├── models/       # Data schemas and SQLAlchemy ORM
│       ├── tools/        # Logic for all MCP tools
│       ├── config.py     # Pydantic Settings & Environment
│       ├── database.py   # SQLAlchemy Engine & Session setup
│       ├── server.py     # MCP App and Entrypoint
│       ├── resources.py  # Live schema inspection logic
│       └── prompts.py    # SQL assistant prompt templates
├── tests/                # Unit and integration tests
└── Makefile              # Development lifecycle automation
```

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

## MCP inspector
```bash
make inspect
```

## Tools

| Tool | Required | Optional | Description |
|---|---|---|---|
| `run_query` | `sql` | — | Execute a read-only SELECT query |
| `add_category` | `name` | `color` | Create a category |
| `list_categories` | — | — | List all categories |
| `add_habit` | `name`, `frequency_type` | `description`, `category_id`, `frequency_target` | Create a habit |
| `list_habits` | — | `category_id`, `include_archived` | List habits |
| `complete_habit` | `habit_id` | `note`, `completed_at` | Log a habit completion |
| `archive_habit` | `habit_id` | `archived_at` | Soft-delete a habit |
| `add_todo` | `title` | `notes`, `priority`, `due_date`, `category_id`, `habit_id` | Create a todo |
| `list_todos` | — | `category_id`, `habit_id`, `completed` | List todos |
| `complete_todo` | `todo_id` | `note`, `completed_at` | Complete a todo, auto-logs habit completion if linked |

## Resources

| URI | Description |
|---|---|
| `db://schema` | Live database schema — tables, columns, foreign keys, indexes |

## Prompts

| Name | Argument | Description |
|---|---|---|
| `sql-assistant` | `focus` (optional) | Primes Claude with full schema knowledge before writing queries |

## Tool access policy

The AI has no delete capabilities by design. Destructive operations
are reserved for direct database access or a future frontend.

To access the database directly:
```bash
make docker-shell
sqlite3 /app/data/habit_tracker.db
```

## ⚠️ Warnings

- `docker-compose down -v` permanently destroys the database and all data
- `READ_ONLY_MODE=true` blocks all write operations including dedicated write tools
- Never use `run_query` for writes — use the dedicated write tools instead
