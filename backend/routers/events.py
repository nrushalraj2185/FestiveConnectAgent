from fastapi import APIRouter, status
from typing import List
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
