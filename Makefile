install:
	uv sync --group dev

test:
	uv run pytest tests/ --cov=src --cov-report=term-missing

test-fast:
	uv run pytest tests/ -x

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

typecheck:
	uv run mypy src/

check: lint typecheck test

seed:
	uv run python scripts/seed.py

run:
	uv run python -m habit_tracker_mcp.server
