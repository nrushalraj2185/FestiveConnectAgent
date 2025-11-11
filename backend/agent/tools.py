from fastapi import HTTPException
from models.data_models import Event
from repos.repo import Repo
from services.service import Service

repo = Repo()
service = Service(repo)

async def get_all_events() -> dict:
    """Get all events"""
    return await service.get_all_events()

