#!/bin/bash
set -e

# Always run migrations on startup
echo "Running database migrations..."
alembic upgrade head

# If arguments are provided, execute them. Otherwise start the server.
if [ "$#" -gt 0 ]; then
    echo "Executing command: $@"
    exec "$@"
else
    echo "Starting MCP server..."
    exec python -m habit_tracker_mcp.server
fi
