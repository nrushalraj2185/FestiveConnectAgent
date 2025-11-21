from typing import List, Union, Any, Optional
from fastapi import HTTPException
from models.data_models import Event
from repos.repo import Repo
from uuid import uuid4
from datetime import datetime, timedelta
from collections import Counter

EventLike = Union[Event, dict]

def _event_field(event: EventLike, field: str, default: Any = None):
    if isinstance(event, dict):
        return event.get(field, default)
    return getattr(event, field, default)

def _event_dict(event: EventLike) -> dict:
    if isinstance(event, dict):
        return event
    return event.dict()

def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        try:
            return datetime.strptime(value.strip().split()[0], "%Y-%m-%d")
        except Exception:
            return None

class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    # -----------------------------------------------------
    # CRUD OPERATIONS
    # -----------------------------------------------------

    async def create_event(self, event: Event) -> Event:
        """Create a new event"""
        await self.repo.init_db()

        event_data = event.dict() if hasattr(event, "dict") else dict(event)

        # Add unique ID and created_at timestamp
        event_data["id"] = event_data.get("id") or str(uuid4())
        timestamp = datetime.now().isoformat()
        event_data["created_at"] = event_data.get("created_at") or timestamp
        event_data["updated_at"] = event_data.get("updated_at") or timestamp

        existing = await self.repo.get(event_data["id"])
        if existing:
            raise HTTPException(status_code=409, detail="Event already exists")

        await self.repo.insert(event_data)
        return Event(**event_data)

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

    async def update_event(self, event_id: str, event: Event) -> Event:
        """Update existing event"""
        await self.repo.init_db()
        event_data = event.dict() if hasattr(event, "dict") else dict(event)
        event_data["id"] = event_id
        event_data["updated_at"] = datetime.now().isoformat()
        updated = await self.repo.update(event_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Event not found to update")
        return Event(**event_data)

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
            date_str = (
                _event_field(e, "date")
                or _event_field(e, "event_date")
                or _event_field(e, "created_at")
            )
            if not date_str:
                continue
            try:
                d = _parse_datetime(date_str)
                if not d:
                    continue
                if d.month == now.month and d.year == now.year:
                    monthly.append(e)
            except Exception:
                continue
        return monthly

    async def get_city_with_most_events(self) -> dict:
        await self.repo.init_db()
        events = await self.repo.list()
        cities = [
            _event_field(e, "city") or _event_field(e, "location")
            for e in events
            if _event_field(e, "city") or _event_field(e, "location")
        ]
        if not cities:
            return {"city": None, "count": 0}
        city, count = Counter(cities).most_common(1)[0]
        return {"city": city, "count": count}

    async def get_top_performer(self) -> dict:
        await self.repo.init_db()
        events = await self.repo.list()
        performers = []
        for e in events:
            perf_list = _event_field(e, "performers") or []
            if isinstance(perf_list, (list, tuple, set)):
                performers.extend(p.strip() for p in perf_list if p)
                continue
            performer = _event_field(e, "performer") or _event_field(e, "artist")
            if performer:
                performers.append(performer.strip())
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
                dt = _parse_datetime(_event_field(e, key))
                if dt:
                    return dt
            return datetime.min

        most_recent = max(events, key=parse_date)
        return _event_dict(most_recent)

    async def get_recent_events_15_days(self, days: int = 15) -> List[Event]:
        """List all events created in the last `days` days (default 15)."""
        await self.repo.init_db()
        events = await self.repo.list()
        cutoff = datetime.now() - timedelta(days=days)

        recent = []
        for e in events:
            for key in ["created_at", "date", "event_date"]:
                try:
                    value = _event_field(e, key)
                    dt = _parse_datetime(value)
                    if dt and dt >= cutoff:
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
                    dt = _parse_datetime(_event_field(e, key))
                    if dt and dt < now:
                        past_locations.append(
                            _event_field(e, "location") or _event_field(e, "city")
                        )
                        break
                except Exception:
                    continue

        if not past_locations:
            return {"location": None, "count": 0}
        location, count = Counter(past_locations).most_common(1)[0]
        return {"location": location, "count": count}

