from fastapi import HTTPException
from models.data_models import Event
from repos.repo import Repo
from services.service import Service

repo = Repo()
service = Service(repo)

# -----------------------------------------------------
# CRUD OPERATIONS
# -----------------------------------------------------

async def get_all_events() -> dict:
    return await service.get_all_events()

async def create_event(event: Event) -> dict:
    return await service.create_event(event)

async def get_event(event_id: str) -> Event:
    return await service.get_event(event_id)

async def update_event(event_id: str, event: Event):
    return await service.update_event(event_id, event)

async def delete_event(event_id: str):
    return await service.delete_event(event_id)

# -----------------------------------------------------
# ANALYTICAL OPERATIONS
# -----------------------------------------------------

async def get_total_events() -> int:
    return await service.get_total_events()

async def get_events_this_month() -> list:
    return await service.get_events_this_month()

async def get_city_with_most_events() -> dict:
    return await service.get_city_with_most_events()

async def get_top_performer() -> dict:
    return await service.get_top_performer()

async def get_most_recent_event() -> dict:
    return await service.get_most_recent_event()

async def get_recent_events_15_days() -> list:
    return await service.get_recent_events_15_days()

async def get_location_with_most_past_events() -> dict:
    return await service.get_location_with_most_past_events()
