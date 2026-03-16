import re

MUTATION_KEYWORDS = {"insert", "update", "delete", "drop", "alter", "truncate", "replace"}


def _strip_leading_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip()


def check_query_allowed(sql: str, read_only_mode: bool) -> None:
    """Raise ValueError if the query is not allowed in the current mode."""
    if not sql.strip():
        raise ValueError("SQL query is empty")

    cleaned = _strip_leading_comments(sql)

    if not cleaned:
        raise ValueError("SQL query contains only comments")

    first_keyword = cleaned.split()[0].lower()

    if read_only_mode and first_keyword in MUTATION_KEYWORDS:
        raise ValueError(
            f"Server is in read-only mode. '{first_keyword.upper()}' statements are not permitted."
        )
