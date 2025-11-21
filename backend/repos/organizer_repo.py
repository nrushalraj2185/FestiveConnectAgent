import aiosqlite
from typing import List, Optional

from constants import DB_NAME, ORGANIZER_TABLE_NAME
from models.data_models import Organizer


class OrganizerRepo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {ORGANIZER_TABLE_NAME} (
                    organizer_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    company TEXT NOT NULL,
                    region TEXT NOT NULL,
                    experience INTEGER DEFAULT 0,
                    managed_events INTEGER DEFAULT 0,
                    cultural_events INTEGER DEFAULT 0,
                    events_2025 INTEGER DEFAULT 0
                )
            """
            )
            await db.commit()

    async def insert(self, organizer: Organizer):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                INSERT INTO {ORGANIZER_TABLE_NAME}
                    (organizer_id, name, company, region, experience, managed_events, cultural_events, events_2025)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    organizer.organizer_id,
                    organizer.name,
                    organizer.company,
                    organizer.region,
                    organizer.experience,
                    organizer.managed_events,
                    organizer.cultural_events,
                    organizer.events_2025,
                ),
            )
            await db.commit()

    async def list(self) -> List[Organizer]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT organizer_id, name, company, region, experience, managed_events, cultural_events, events_2025
                FROM {ORGANIZER_TABLE_NAME}
            """
            )
            rows = await cursor.fetchall()
            return [
                Organizer(
                    organizer_id=row[0],
                    name=row[1],
                    company=row[2],
                    region=row[3],
                    experience=row[4],
                    managed_events=row[5],
                    cultural_events=row[6],
                    events_2025=row[7],
                )
                for row in rows
            ]

    async def get(self, organizer_id: str) -> Optional[Organizer]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT organizer_id, name, company, region, experience, managed_events, cultural_events, events_2025
                FROM {ORGANIZER_TABLE_NAME}
                WHERE organizer_id = ?
            """,
                (organizer_id,),
            )
            row = await cursor.fetchone()
            if row:
                return Organizer(
                    organizer_id=row[0],
                    name=row[1],
                    company=row[2],
                    region=row[3],
                    experience=row[4],
                    managed_events=row[5],
                    cultural_events=row[6],
                    events_2025=row[7],
                )
            return None

    async def update(self, organizer: Organizer) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            before = db.total_changes
            await db.execute(
                f"""
                UPDATE {ORGANIZER_TABLE_NAME}
                SET name = ?, company = ?, region = ?, experience = ?, managed_events = ?, cultural_events = ?, events_2025 = ?
                WHERE organizer_id = ?
            """,
                (
                    organizer.name,
                    organizer.company,
                    organizer.region,
                    organizer.experience,
                    organizer.managed_events,
                    organizer.cultural_events,
                    organizer.events_2025,
                    organizer.organizer_id,
                ),
            )
            await db.commit()
            return (db.total_changes - before) > 0

    async def delete(self, organizer_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            before = db.total_changes
            await db.execute(
                f"DELETE FROM {ORGANIZER_TABLE_NAME} WHERE organizer_id = ?",
                (organizer_id,),
            )
            await db.commit()
            return db.total_changes - before

    async def events_managed_by_company(self, company: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT COALESCE(SUM(managed_events), 0)
                FROM {ORGANIZER_TABLE_NAME}
                WHERE LOWER(company) = LOWER(?)
            """,
                (company,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def region_with_max_cultural_events(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT region, SUM(cultural_events) as total_cultural
                FROM {ORGANIZER_TABLE_NAME}
                GROUP BY region
                ORDER BY total_cultural DESC
                LIMIT 1
            """
            )
            row = await cursor.fetchone()
            if not row:
                return {"region": None, "cultural_events": 0}
            return {"region": row[0], "cultural_events": row[1]}

    async def top_organizer_2025(self) -> Optional[Organizer]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT organizer_id, name, company, region, experience, managed_events, cultural_events, events_2025
                FROM {ORGANIZER_TABLE_NAME}
                ORDER BY events_2025 DESC
                LIMIT 1
            """
            )
            row = await cursor.fetchone()
            if row:
                return Organizer(
                    organizer_id=row[0],
                    name=row[1],
                    company=row[2],
                    region=row[3],
                    experience=row[4],
                    managed_events=row[5],
                    cultural_events=row[6],
                    events_2025=row[7],
                )
            return None

