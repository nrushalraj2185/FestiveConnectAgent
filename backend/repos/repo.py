import aiosqlite
from typing import List, Optional
from models.data_models import Event
from constants import DB_NAME, TABLE_NAME

class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initialize the events table."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    performers TEXT,
                    description TEXT
                )
            """)
            await db.commit()

    async def insert(self, event: Event):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                INSERT INTO {TABLE_NAME} (id, title, date, location, performers, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.title,
                event.date,
                event.location,
                ",".join(event.performers),
                event.description
            ))
            await db.commit()

    async def list(self) -> List[Event]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, title, date, location, performers, description FROM {TABLE_NAME}")
            rows = await cursor.fetchall()
            return [
                Event(
                    id=row[0],
                    title=row[1],
                    date=row[2],
                    location=row[3],
                    performers=row[4].split(",") if row[4] else [],
                    description=row[5]
                )
                for row in rows
            ]

    async def get(self, event_id: str) -> Optional[Event]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                SELECT id, title, date, location, performers, description
                FROM {TABLE_NAME}
                WHERE id = ?
            """, (event_id,))
            row = await cursor.fetchone()
            if row:
                return Event(
                    id=row[0],
                    title=row[1],
                    date=row[2],
                    location=row[3],
                    performers=row[4].split(",") if row[4] else [],
                    description=row[5]
                )
            return None

    async def update(self, event: Event) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                UPDATE {TABLE_NAME}
                SET title = ?, date = ?, location = ?, performers = ?, description = ?
                WHERE id = ?
            """, (
                event.title,
                event.date,
                event.location,
                ",".join(event.performers),
                event.description,
                event.id
            ))
            await db.commit()
            return cursor.rowcount > 0

    async def delete(self, event_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (event_id,))
            await db.commit()
            return cursor.rowcount
