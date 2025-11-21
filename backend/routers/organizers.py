from fastapi import APIRouter, status, Query, Response
from typing import List, Dict, Any

from constants import DB_NAME
from models.data_models import Organizer
from repos.organizer_repo import OrganizerRepo
from services.organizer_service import OrganizerService


router = APIRouter()
repo = OrganizerRepo(DB_NAME)
service = OrganizerService(repo)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Organizer)
async def create_organizer(organizer: Organizer):
    """Create a new organizer entry."""
    return await service.create_organizer(organizer)


@router.get("/", response_model=List[Organizer])
async def list_organizers():
    """List all organizers."""
    return await service.list_organizers()


@router.get("/{organizer_id}", response_model=Organizer)
async def get_organizer(organizer_id: str):
    """Get a single organizer by ID."""
    return await service.get_organizer(organizer_id)


@router.put("/{organizer_id}", response_model=Organizer)
async def update_organizer(organizer_id: str, organizer: Organizer):
    """Update organizer information."""
    return await service.update_organizer(organizer_id, organizer)


@router.delete("/{organizer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organizer(organizer_id: str):
    """Delete an organizer."""
    await service.delete_organizer(organizer_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Analytics

@router.get("/analytics/company-events")
async def company_events(company: str = Query(..., description="Company name")):
    """Return how many events are managed by a given company."""
    return await service.events_managed_by_company(company)


@router.get("/analytics/top-region")
async def top_region_for_cultural_events():
    """Return region hosting maximum cultural events."""
    return await service.region_with_max_cultural_events()


@router.get("/analytics/top-organizer-2025")
async def top_organizer_2025():
    """Return organizer handling the most events in 2025."""
    organizer = await service.top_organizer_2025()
    if not organizer:
        return {"organizer": None, "events_2025": 0}
    return {"organizer": organizer, "events_2025": organizer.events_2025}

