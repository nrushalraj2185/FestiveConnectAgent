import aiosqlite
from typing import Any, Dict, List, Optional, Union
from models.data_models import Event
from constants import DB_NAME, TABLE_NAME


class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initialize the events table and ensure auditing columns exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    performers TEXT,
                    description TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )
            await db.commit()

            # Ensure the table has the newly added columns if it pre-existed
            await self._ensure_column(db, "created_at", "TEXT")
            await self._ensure_column(db, "updated_at", "TEXT")

    async def _ensure_column(self, db, column_name: str, column_type: str):
        cursor = await db.execute(f"PRAGMA table_info({TABLE_NAME})")
        columns = [row[1] for row in await cursor.fetchall()]
        if column_name not in columns:
            await db.execute(
                f"ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} {column_type}"
            )
            await db.commit()

    def _normalize_event(self, event: Union[Event, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(event, Event):
            data = event.model_dump()
        else:
            data = dict(event)

        performers = data.get("performers") or []
        if isinstance(performers, str):
            performers = [p.strip() for p in performers.split(",") if p.strip()]
        data["performers"] = performers
        return data

    def _performers_str(self, performers: List[str]) -> str:
        return ",".join([p.strip() for p in performers if p])

    async def insert(self, event: Event):
        data = self._normalize_event(event)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                INSERT INTO {TABLE_NAME} (id, title, date, location, performers, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data.get("id"),
                    data.get("title"),
                    data.get("date"),
                    data.get("location"),
                    self._performers_str(data.get("performers", [])),
                    data.get("description"),
                    data.get("created_at"),
                    data.get("updated_at"),
                ),
            )
            await db.commit()

    async def list(self) -> List[Event]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"SELECT id, title, date, location, performers, description, created_at, updated_at FROM {TABLE_NAME}"
            )
            rows = await cursor.fetchall()
            return [
                Event(
                    id=row[0],
                    title=row[1],
                    date=row[2],
                    location=row[3],
                    performers=row[4].split(",") if row[4] else [],
                    description=row[5],
                    created_at=row[6],
                    updated_at=row[7],
                )
                for row in rows
            ]

    async def get(self, event_id: str) -> Optional[Event]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT id, title, date, location, performers, description, created_at, updated_at
                FROM {TABLE_NAME}
                WHERE id = ?
            """,
                (event_id,),
            )
            row = await cursor.fetchone()
            if row:
                return Event(
                    id=row[0],
                    title=row[1],
                    date=row[2],
                    location=row[3],
                    performers=row[4].split(",") if row[4] else [],
                    description=row[5],
                    created_at=row[6],
                    updated_at=row[7],
                )
            return None

    async def update(self, event: Event) -> bool:
        data = self._normalize_event(event)
        async with aiosqlite.connect(self.db_path) as db:
            before = db.total_changes
            await db.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET title = ?, date = ?, location = ?, performers = ?, description = ?, updated_at = ?
                WHERE id = ?
            """,
                (
                    data.get("title"),
                    data.get("date"),
                    data.get("location"),
                    self._performers_str(data.get("performers", [])),
                    data.get("description"),
                    data.get("updated_at"),
                    data.get("id"),
                ),
            )
            await db.commit()
            return (db.total_changes - before) > 0

    async def delete(self, event_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            before = db.total_changes
            await db.execute(
                f"DELETE FROM {TABLE_NAME} WHERE id = ?", (event_id,)
            )
            await db.commit()
            return db.total_changes - before
