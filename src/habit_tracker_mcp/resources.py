from mcp.types import Resource, TextResourceContents
from pydantic import AnyUrl
from sqlalchemy import Inspector
from sqlalchemy import inspect as sa_inspect

from habit_tracker_mcp.database import engine

SCHEMA_RESOURCE = Resource(
    uri=AnyUrl("db://schema"),
    name="Database schema",
    description="Live schema of all tables in the habit tracker database",
    mimeType="text/plain",
)


def get_schema_contents() -> TextResourceContents:
    """Introspect the live database and return schema as markdown."""
    inspector: Inspector = sa_inspect(engine)
    table_names = inspector.get_table_names()

    lines: list[str] = [
        "# Habit tracker database schema\n",
        f"Tables: {', '.join(table_names)}\n",
    ]

    for table_name in table_names:
        lines.append(f"\n## {table_name}\n")
        columns = inspector.get_columns(table_name)
        for col in columns:
            nullable = "" if col["nullable"] else " NOT NULL"
            default = f" DEFAULT {col['default']}" if col.get("default") else ""
            lines.append(f"- {col['name']}: {col['type']}{nullable}{default}\n")

        fks = inspector.get_foreign_keys(table_name)
        if fks:
            lines.append("\nForeign keys:\n")
            for fk in fks:
                lines.append(
                    f"- {fk['constrained_columns']} → "
                    f"{fk['referred_table']}.{fk['referred_columns']}\n"
                )

        indexes = inspector.get_indexes(table_name)
        if indexes:
            lines.append("\nIndexes:\n")
            for idx in indexes:
                lines.append(f"- {idx['name']}: {idx['column_names']}\n")

    return TextResourceContents(
        uri=AnyUrl("db://schema"),
        mimeType="text/plain",
        text="".join(lines),
    )
