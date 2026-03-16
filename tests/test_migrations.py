from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


def test_upgrade_creates_all_tables() -> None:
    engine = create_engine("sqlite:///:memory:")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

    with engine.begin() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    tables = inspect(engine).get_table_names()
    assert "habits" in tables
    assert "todos" in tables
    assert "categories" in tables
    assert "habit_completions" in tables


def test_downgrade_removes_all_tables() -> None:
    engine = create_engine("sqlite:///:memory:")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

    with engine.begin() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    with engine.begin() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.downgrade(alembic_cfg, "base")

    assert inspect(engine).get_table_names() == ["alembic_version"]


def test_upgrade_creates_indexes() -> None:
    engine = create_engine("sqlite:///:memory:")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

    with engine.begin() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    inspector = inspect(engine)
    completion_indexes = [i["name"] for i in inspector.get_indexes("habit_completions")]
    assert "ix_habit_completions_id" in completion_indexes
