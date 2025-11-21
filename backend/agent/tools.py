# tools.py
from typing import List, Dict, Any, Optional, Union
from models.data_models import Event, Organizer
from repos.repo import Repo
from repos.organizer_repo import OrganizerRepo
from services.service import Service
from services.organizer_service import OrganizerService

repo = Repo()
service = Service(repo)

organizer_repo = OrganizerRepo()
organizer_service = OrganizerService(organizer_repo)

# --- existing helpers ---
def _event_to_dict(e: Union[Event, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(e, dict):
        data = e
    else:
        data = e.dict()
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "date": data.get("date"),
        "location": data.get("location"),
        "performers": data.get("performers") or [],
        "description": data.get("description") or "",
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }

# reuse earlier tools if present or keep here for completeness
async def get_all_events() -> List[Dict[str, Any]]:
    events = await service.get_all_events()
    return [_event_to_dict(e) for e in events]

async def create_event_tool(event_data: Dict[str, Any]) -> Dict[str, Any]:
    required = ["title", "date", "location"]
    missing = [f for f in required if f not in event_data or not event_data[f]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    ev = Event(
        title=event_data["title"],
        date=event_data["date"],
        location=event_data["location"],
        performers=event_data.get("performers", []),
        description=event_data.get("description", "")
    )
    created = await service.create_event(ev)
    return _event_to_dict(created)

async def events_by_location(location: str) -> List[Dict[str, Any]]:
    location_l = (location or "").strip().lower()
    all_events = await service.get_all_events()
    filtered = [e for e in all_events if location_l in (e.location or "").lower()]
    return [_event_to_dict(e) for e in filtered]

async def events_by_month(month: str) -> List[Dict[str, Any]]:
    # same implementation as before (keeps month matching tolerant)
    if not month:
        return []
    month = month.strip()
    # try parse numeric
    month_num: Optional[int] = None
    if month.isdigit():
        try:
            month_num = int(month)
            if not 1 <= month_num <= 12:
                month_num = None
        except:
            month_num = None
    else:
        # map textual months to numbers (short list)
        mapping = {
            "january":1,"jan":1,"february":2,"feb":2,"march":3,"mar":3,
            "april":4,"apr":4,"may":5,"june":6,"jun":6,"july":7,"jul":7,
            "august":8,"aug":8,"september":9,"sep":9,"october":10,"oct":10,
            "november":11,"nov":11,"december":12,"dec":12
        }
        if month.lower() in mapping:
            month_num = mapping[month.lower()]

    all_events = await service.get_all_events()
    result = []
    for e in all_events:
        date_str = (e.date or "").lower()
        if month_num is not None:
            # match patterns like YYYY-MM-DD containing -MM-
            if f"-{month_num:02d}-" in date_str or f"/{month_num:02d}/" in date_str:
                result.append(e)
                continue
        # fallback: match month name substring
        if month.lower() in date_str:
            result.append(e)
            continue
    return [_event_to_dict(ev) for ev in result]

async def check_event_exists(title: str) -> Dict[str, Any]:
    if not title:
        return {"exists": False, "event": None}
    all_events = await service.get_all_events()
    for e in all_events:
        if (e.title or "").strip().lower() == title.strip().lower():
            return {"exists": True, "event": _event_to_dict(e)}
    return {"exists": False, "event": None}

async def update_event_location(title: str, new_location: str) -> Dict[str, Any]:
    if not title:
        raise ValueError("Title required")
    all_events = await service.get_all_events()
    target = None
    for e in all_events:
        if (e.title or "").strip().lower() == title.strip().lower():
            target = e
            break
    if not target:
        raise LookupError(f"Event titled '{title}' not found")
    target.location = new_location
    updated = await service.update_event(target.id, target)
    return _event_to_dict(updated)

async def delete_event_by_title(title: str) -> Dict[str, Any]:
    if not title:
        raise ValueError("Title required")
    all_events = await service.get_all_events()
    target = None
    for e in all_events:
        if (e.title or "").strip().lower() == title.strip().lower():
            target = e
            break
    if not target:
        raise LookupError(f"Event titled '{title}' not found")
    await service.delete_event(target.id)
    return {"deleted": True, "deleted_event": _event_to_dict(target)}

# -------------------------------
# New analytics tools (added here)
# -------------------------------

async def total_events_count() -> Dict[str, int]:
    """Return total number of events."""
    total = await service.get_total_events()
    return {"total_events": total}

async def events_this_month() -> Dict[str, Any]:
    """Return events happening in the current month."""
    monthly_events = await service.get_events_this_month()
    return {
        "count": len(monthly_events),
        "events": [_event_to_dict(ev) for ev in monthly_events],
    }

async def city_with_most_events() -> Dict[str, Any]:
    """Return the city (location) hosting the most events."""
    return await service.get_city_with_most_events()

async def top_performer() -> Dict[str, Any]:
    """Return the performer appearing most frequently."""
    return await service.get_top_performer()

async def most_recently_added_event() -> Dict[str, Any]:
    """Return the single most recently created event."""
    recent = await service.get_most_recent_event()
    if not recent or (isinstance(recent, dict) and recent.get("message")):
        return {"most_recent": None}
    return {
        "most_recent": recent
        if isinstance(recent, dict)
        else _event_to_dict(recent)
    }

async def events_created_last_n_days(n: int = 15) -> Dict[str, Any]:
    """Return events created within the last N days (default 15)."""
    events = await service.get_recent_events_15_days(days=n)
    return {"count": len(events), "events": [_event_to_dict(ev) for ev in events]}

async def location_with_most_past_events() -> Dict[str, Any]:
    """Return the location that has hosted the most past events."""
    return await service.get_location_with_most_past_events()


# -------------------------------
# Organizer (Challenge 5) tools
# -------------------------------

def _organizer_to_dict(org: Union[Organizer, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(org, dict):
        data = org
    else:
        data = org.dict()
    return data


async def create_organizer_tool(organizer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new organizer entry."""
    organizer = Organizer(**organizer_data)
    created = await organizer_service.create_organizer(organizer)
    return _organizer_to_dict(created)


async def list_organizers_tool() -> List[Dict[str, Any]]:
    """List organizers."""
    organizers = await organizer_service.list_organizers()
    return [_organizer_to_dict(org) for org in organizers]


async def events_managed_by_company_tool(company: str) -> Dict[str, Any]:
    """Return how many events are managed by a given company."""
    return await organizer_service.events_managed_by_company(company)


async def region_with_max_cultural_events_tool() -> Dict[str, Any]:
    """Return the region with the maximum number of cultural events."""
    return await organizer_service.region_with_max_cultural_events()


async def top_organizer_2025_tool() -> Dict[str, Any]:
    """Return the organizer handling the most events in 2025."""
    organizer = await organizer_service.top_organizer_2025()
    if not organizer:
        return {"organizer": None, "events_2025": 0}
    data = _organizer_to_dict(organizer)
    data["events_2025"] = organizer.events_2025
    return {"organizer": data, "events_2025": organizer.events_2025}
