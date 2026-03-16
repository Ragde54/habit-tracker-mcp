from typing import Any

from mcp.types import TextContent

from habit_tracker_mcp.prompts import get_sql_assistant


def test_prompt_contains_schema(override_engine: Any) -> None:
    result = get_sql_assistant()
    content = result.messages[0].content
    assert isinstance(content, TextContent)
    text = content.text
    assert "habits" in text
    assert "todos" in text


def test_prompt_with_focus(override_engine: Any) -> None:
    result = get_sql_assistant(focus="streaks")
    content = result.messages[0].content
    assert isinstance(content, TextContent)
    text = content.text
    assert "streaks" in text


def test_prompt_without_focus_has_no_focus_instruction(override_engine: Any) -> None:
    result = get_sql_assistant()
    content = result.messages[0].content
    assert isinstance(content, TextContent)
    text = content.text
    assert "Focus particularly" not in text


def test_prompt_includes_write_tool_guidance(override_engine: Any) -> None:
    result = get_sql_assistant()
    content = result.messages[0].content
    assert isinstance(content, TextContent)
    text = content.text
    assert "run_query" in text
    assert "mutations" in text


def test_prompt_has_one_message(override_engine: Any) -> None:
    result = get_sql_assistant()
    assert len(result.messages) == 1


def test_prompt_message_role_is_user(override_engine: Any) -> None:
    result = get_sql_assistant()
    assert result.messages[0].role == "user"
