from typing import Generator

import pytest
from alembic.config import Config
from pytest import MonkeyPatch
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command


def build_test_engine() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

    with engine.begin() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")
    return engine


@pytest.fixture(scope="function")
def db_engine() -> Generator[Engine, None, None]:
    engine = build_test_engine()
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def override_engine(db_engine: Engine, monkeypatch: MonkeyPatch) -> Engine:
    import habit_tracker_mcp.database as db_module
    import habit_tracker_mcp.tools.add_category as add_category_module
    import habit_tracker_mcp.tools.add_habit as add_habit_module
    import habit_tracker_mcp.tools.add_todo as add_todo_module
    import habit_tracker_mcp.tools.archive_habit as archive_habit_module
    import habit_tracker_mcp.tools.complete_habit as complete_habit_module
    import habit_tracker_mcp.tools.complete_todo as complete_todo_module
    import habit_tracker_mcp.tools.list_categories as list_categories_module
    import habit_tracker_mcp.tools.list_habits as list_habits_module
    import habit_tracker_mcp.tools.list_todos as list_todos_module
    import habit_tracker_mcp.tools.run_query as run_query_module

    for mod in [
        db_module,
        add_category_module,
        add_habit_module,
        add_todo_module,
        archive_habit_module,
        complete_habit_module,
        complete_todo_module,
        list_categories_module,
        list_habits_module,
        list_todos_module,
        run_query_module,
    ]:
        monkeypatch.setattr(mod, "engine", db_engine)

    return db_engine
