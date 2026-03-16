import pytest

from habit_tracker_mcp.security import check_query_allowed


def test_select_allowed_read_only() -> None:
    check_query_allowed("SELECT * FROM habits", read_only_mode=True)


def test_select_allowed_write_mode() -> None:
    check_query_allowed("SELECT * FROM habits", read_only_mode=False)


def test_empty_query_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        check_query_allowed("   ", read_only_mode=False)


def test_comment_only_raises() -> None:
    with pytest.raises(ValueError, match="comments"):
        check_query_allowed("-- just a comment", read_only_mode=False)


def test_comment_before_mutation_blocked() -> None:
    with pytest.raises(ValueError, match="read-only"):
        check_query_allowed("-- comment\nDROP TABLE habits", read_only_mode=True)


def test_insert_allowed_write_mode() -> None:
    check_query_allowed("INSERT INTO habits VALUES (1)", read_only_mode=False)


@pytest.mark.parametrize(
    "keyword", ["insert", "update", "delete", "drop", "alter", "truncate", "replace"]
)
def test_all_mutations_blocked_read_only(keyword: str) -> None:
    with pytest.raises(ValueError, match="read-only"):
        check_query_allowed(f"{keyword} INTO habits VALUES (1)", read_only_mode=True)


def test_case_insensitive_blocking() -> None:
    with pytest.raises(ValueError, match="read-only"):
        check_query_allowed("DROP TABLE habits", read_only_mode=True)
    with pytest.raises(ValueError, match="read-only"):
        check_query_allowed("drop table habits", read_only_mode=True)
