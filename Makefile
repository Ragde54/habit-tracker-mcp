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

inspect:
	npx @modelcontextprotocol/inspector uv run python -m habit_tracker_mcp.server

docker-build:
	docker build -f docker/Dockerfile -t habit-tracker-mcp .

docker-run:
	docker-compose -f docker/docker-compose.yml up

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-shell:
	docker-compose -f docker/docker-compose.yml run --rm habit-tracker-mcp /bin/bash

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

inspect-docker:
	npx @modelcontextprotocol/inspector docker-compose run --rm -T habit-tracker-mcp
