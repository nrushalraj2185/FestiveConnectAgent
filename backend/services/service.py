from typing import List
from fastapi import HTTPException
from models.data_models import Event
from repos.repo import Repo
from uuid import uuid4
from datetime import datetime, timedelta
from collections import Counter

class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    # -----------------------------------------------------
    # CRUD OPERATIONS
    # -----------------------------------------------------

    async def create_event(self, event: Event):
        """Create a new event"""
        await self.repo.init_db()

        event_data = event.dict() if hasattr(event, "dict") else dict(event)

        # Add unique ID and created_at timestamp
        event_data["id"] = event_data.get("id", str(uuid4()))
        event_data["created_at"] = event_data.get("created_at", datetime.now().isoformat())

        existing = await self.repo.get(event_data["id"])
        if existing:
            raise HTTPException(status_code=409, detail="Event already exists")

        await self.repo.insert(event_data)
        return event_data

    async def get_all_events(self) -> List[Event]:
        """Return all events"""
        await self.repo.init_db()
        return await self.repo.list()

    async def get_event(self, event_id: str) -> Event:
        """Return single event by ID"""
        await self.repo.init_db()
        event = await self.repo.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    async def update_event(self, event_id: str, event: Event):
        """Update existing event"""
        await self.repo.init_db()
        event_data = event.dict() if hasattr(event, "dict") else dict(event)
        event_data["id"] = event_id
        updated = await self.repo.update(event_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Event not found to update")
        return event_data

    async def delete_event(self, event_id: str):
        """Delete event"""
        await self.repo.init_db()
        deleted = await self.repo.delete(event_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Event not found to delete")
        return None

    # -----------------------------------------------------
    # ANALYTICAL FUNCTIONS
    # -----------------------------------------------------

    async def get_total_events(self) -> int:
        await self.repo.init_db()
        events = await self.repo.list()
        return len(events)

    async def get_events_this_month(self) -> List[Event]:
        await self.repo.init_db()
        events = await self.repo.list()
        now = datetime.now()

        monthly = []
        for e in events:
            date_str = e.get("date") or e.get("event_date") or e.get("created_at")
            if not date_str:
                continue
            try:
                d = datetime.fromisoformat(date_str)
                if d.month == now.month and d.year == now.year:
                    monthly.append(e)
            except Exception:
                continue
        return monthly

    async def get_city_with_most_events(self) -> dict:
        await self.repo.init_db()
        events = await self.repo.list()
        cities = [e.get("city") or e.get("location") for e in events if e.get("city") or e.get("location")]
        if not cities:
            return {"city": None, "count": 0}
        city, count = Counter(cities).most_common(1)[0]
        return {"city": city, "count": count}

    async def get_top_performer(self) -> dict:
        await self.repo.init_db()
        events = await self.repo.list()
        performers = [e.get("performer") or e.get("artist") for e in events if e.get("performer") or e.get("artist")]
        if not performers:
            return {"performer": None, "count": 0}
        performer, count = Counter(performers).most_common(1)[0]
        return {"performer": performer, "count": count}

    async def get_most_recent_event(self) -> dict:
        """Find the event added most recently"""
        await self.repo.init_db()
        events = await self.repo.list()
        if not events:
            return {"message": "No events found"}

        def parse_date(e):
            for key in ["created_at", "date", "event_date"]:
                try:
                    if e.get(key):
                        return datetime.fromisoformat(e[key])
                except Exception:
                    continue
            return datetime.min

        most_recent = max(events, key=parse_date)
        return most_recent

    async def get_recent_events_15_days(self) -> List[Event]:
        """List all events created in last 15 days"""
        await self.repo.init_db()
        events = await self.repo.list()
        cutoff = datetime.now() - timedelta(days=15)

        recent = []
        for e in events:
            for key in ["created_at", "date", "event_date"]:
                try:
                    if e.get(key) and datetime.fromisoformat(e[key]) >= cutoff:
                        recent.append(e)
                        break
                except Exception:
                    continue
        return recent

    async def get_location_with_most_past_events(self) -> dict:
        """Find which location hosted the most past events"""
        await self.repo.init_db()
        events = await self.repo.list()
        now = datetime.now()

        past_locations = []
        for e in events:
            for key in ["date", "event_date"]:
                try:
                    if e.get(key) and datetime.fromisoformat(e[key]) < now:
                        past_locations.append(e.get("location") or e.get("city"))
                        break
                except Exception:
                    continue

        if not past_locations:
            return {"location": None, "count": 0}
        location, count = Counter(past_locations).most_common(1)[0]
        return {"location": location, "count": count}

