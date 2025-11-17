# tools.py
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from models.data_models import Event
from repos.repo import Repo
from services.service import Service
from collections import Counter, defaultdict

repo = Repo()
service = Service(repo)

# --- existing helpers ---
def _event_to_dict(e: Event) -> Dict[str, Any]:
    return {
        "id": e.id,
        "title": e.title,
        "date": e.date,
        "location": e.location,
        "performers": e.performers or [],
        "description": e.description or ""
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
    """
    Return total number of events.
    """
    all_events = await service.get_all_events()
    return {"total_events": len(all_events)}

async def events_this_month() -> Dict[str, Any]:
    """
    Count events whose date string contains the current month (loose matching).
    Returns count and list of events (as dicts).
    """
    now = datetime.utcnow()
    month_num = now.month
    all_events = await service.get_all_events()
    matched = []
    for e in all_events:
        ds = (e.date or "").lower()
        if f"-{month_num:02d}-" in ds or f"/{month_num:02d}/" in ds or any(m in ds for m in [now.strftime("%B").lower(), now.strftime("%b").lower()]):
            matched.append(e)
    return {"count": len(matched), "events": [_event_to_dict(ev) for ev in matched]}

async def city_with_most_events() -> Dict[str, Any]:
    """
    Return city (location) with the most events and the count.
    If multiple tie, returns list of top cities.
    """
    all_events = await service.get_all_events()
    # normalize location string (case-insensitive, strip)
    loc_counts = Counter((e.location or "").strip() for e in all_events if e.location)
    if not loc_counts:
        return {"top_cities": [], "max_count": 0}
    max_count = max(loc_counts.values())
    top_cities = [loc for loc, cnt in loc_counts.items() if cnt == max_count]
    return {"top_cities": top_cities, "max_count": max_count}

async def top_performer() -> Dict[str, Any]:
    """
    Return the performer(s) who appear most frequently across events.
    Expects Event.performers to be an iterable/list of strings.
    """
    all_events = await service.get_all_events()
    perf_counter = Counter()
    for e in all_events:
        performers = e.performers or []
        # normalize performer names
        for p in performers:
            if not p:
                continue
            perf_counter[p.strip()] += 1
    if not perf_counter:
        return {"top_performers": [], "max_count": 0}
    max_count = max(perf_counter.values())
    top_performers = [name for name, cnt in perf_counter.items() if cnt == max_count]
    return {"top_performers": top_performers, "max_count": max_count}
