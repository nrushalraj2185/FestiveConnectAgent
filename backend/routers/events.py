from fastapi import APIRouter, status
from typing import List, Dict, Any
from models.data_models import Event
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME
from fastapi import Response

router = APIRouter()
repo = Repo(DB_NAME)
service = Service(repo)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Event)
async def create_event(event: Event):
    """Create a new festival event"""
    return await service.create_event(event)

@router.get("/", response_model=List[Event])
async def get_all_events():
    """Retrieve all festival events"""
    return await service.get_all_events()

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Retrieve a single event by ID"""
    return await service.get_event(event_id)

@router.put("/{event_id}", response_model=Event)
async def update_event(event_id: str, event: Event):
    """Update an existing event"""
    return await service.update_event(event_id, event)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """Delete an event"""
    await service.delete_event(event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------
# Analytics endpoints (Challenge 3)
# -----------------------------------------------------

@router.get("/analytics/total")
async def total_events() -> Dict[str, int]:
    """Return total number of events"""
    total = await service.get_total_events()
    return {"total_events": total}


@router.get("/analytics/this-month")
async def events_this_month() -> Dict[str, Any]:
    """Return events scheduled for the current month"""
    events = await service.get_events_this_month()
    return {"count": len(events), "events": events}


@router.get("/analytics/top-city")
async def city_with_most_events() -> Dict[str, Any]:
    """Return the city/location hosting the most events"""
    return await service.get_city_with_most_events()


@router.get("/analytics/top-performer")
async def performer_with_most_events() -> Dict[str, Any]:
    """Return the performer appearing in the most events"""
    return await service.get_top_performer()


# -----------------------------------------------------
# Auditing endpoints (Challenge 4)
# -----------------------------------------------------

@router.get("/audit/most-recent")
async def most_recent_event() -> Dict[str, Any]:
    """Return the most recently added event"""
    return await service.get_most_recent_event()


@router.get("/audit/last-15-days")
async def events_last_fifteen_days(days: int = 15) -> Dict[str, Any]:
    """List events created in the last N days (default 15)"""
    events = await service.get_recent_events_15_days(days=days)
    return {"count": len(events), "events": events, "days": days}


@router.get("/audit/top-location")
async def location_with_most_history() -> Dict[str, Any]:
    """Return the location that has hosted the most past events"""
    return await service.get_location_with_most_past_events()
