import asyncio
from importlib.metadata import version
from logging import getLogger
from typing import Any, cast

from mcp.server import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptsCapability,
    Resource,
    ResourcesCapability,
    ServerCapabilities,
    TextContent,
    Tool,
    ToolsCapability,
)
from pydantic import AnyUrl

from habit_tracker_mcp.logging_config import setup_logging
from habit_tracker_mcp.prompts import SQL_ASSISTANT_PROMPT, get_sql_assistant
from habit_tracker_mcp.resources import SCHEMA_RESOURCE, get_schema_contents
from habit_tracker_mcp.tools import (
    add_category,
    add_habit,
    add_todo,
    archive_habit,
    complete_habit,
    complete_todo,
    list_categories,
    list_habits,
    list_todos,
    run_query,
)

app = Server("habit-tracker")
logger = getLogger(__name__)

_TOOL_MODULES = [
    add_category,
    add_habit,
    add_todo,
    archive_habit,
    complete_habit,
    complete_todo,
    list_categories,
    list_habits,
    list_todos,
    run_query,
]
_TOOL_MAP = {module.tool_definition.name: module for module in _TOOL_MODULES}


@app.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
async def list_tools() -> list[Tool]:
    return [m.tool_definition for m in _TOOL_MODULES]


@app.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    logger.info("Calling tool: %s", name)
    if name not in _TOOL_MAP:
        logger.warning("Unknown tool requested: %s", name)
        raise ValueError(f"Tool not found: {name}")
    return cast(list[TextContent], _TOOL_MAP[name].run(arguments))


@app.list_resources()  # type: ignore[no-untyped-call, untyped-decorator]
async def list_resources() -> list[Resource]:
    return [SCHEMA_RESOURCE]


@app.read_resource()  # type: ignore[no-untyped-call, untyped-decorator]
async def read_resource(uri: AnyUrl) -> list[ReadResourceContents]:
    if str(uri) == "db://schema":
        schema = get_schema_contents()
        return [ReadResourceContents(content=schema.text, mime_type="text/plain")]
    raise ValueError(f"Unknown resource: {uri}")


@app.list_prompts()  # type: ignore[no-untyped-call, untyped-decorator]
async def list_prompts() -> list[Prompt]:
    return [SQL_ASSISTANT_PROMPT]


@app.get_prompt()  # type: ignore[no-untyped-call, untyped-decorator]
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    if name == "sql-assistant":
        focus = arguments.get("focus") if arguments else None
        return get_sql_assistant(focus)
    raise ValueError(f"Unknown prompt: {name}")


async def main() -> None:
    setup_logging()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="habit-tracker",
                server_version=version("habit-tracker-mcp"),
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(),
                    resources=ResourcesCapability(),
                    prompts=PromptsCapability(),
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
