import sqlite3
import aiosqlite
from pathlib import Path


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._seed_path = Path(__file__).parent.parent.parent / "data" / "seed.sql"

    async def initialize(self) -> None:
        """Create tables and seed data if the database is empty."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            )
            count = await cursor.fetchone()
            if count[0] == 0:
                sql = self._seed_path.read_text()
                await db.executescript(sql)
                await db.commit()

    async def run_query(self, sql: str) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                cursor = await db.execute(sql)
                await db.commit()

                if cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]
                    rows = await cursor.fetchall()
                    return {"columns": columns, "rows": [list(r) for r in rows]}
                else:
                    return {"columns": [], "rows": [], "rowcount": cursor.rowcount}

            except sqlite3.DatabaseError as e:
                return {"error": str(e), "columns": [], "rows": []}
        
        