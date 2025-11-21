from fastapi import HTTPException
from uuid import uuid4
from typing import List, Optional

from models.data_models import Organizer
from repos.organizer_repo import OrganizerRepo


class OrganizerService:
    def __init__(self, repo: OrganizerRepo):
        self.repo = repo

    async def create_organizer(self, organizer: Organizer) -> Organizer:
        await self.repo.init_db()
        data = organizer.copy()
        data.organizer_id = data.organizer_id or str(uuid4())

        existing = await self.repo.get(data.organizer_id)
        if existing:
            raise HTTPException(
                status_code=409, detail="Organizer with this ID already exists"
            )
        await self.repo.insert(data)
        return data

    async def list_organizers(self) -> List[Organizer]:
        await self.repo.init_db()
        return await self.repo.list()

    async def get_organizer(self, organizer_id: str) -> Organizer:
        await self.repo.init_db()
        organizer = await self.repo.get(organizer_id)
        if not organizer:
            raise HTTPException(status_code=404, detail="Organizer not found")
        return organizer

    async def update_organizer(self, organizer_id: str, organizer: Organizer) -> Organizer:
        await self.repo.init_db()
        data = organizer.copy()
        data.organizer_id = organizer_id
        updated = await self.repo.update(data)
        if not updated:
            raise HTTPException(status_code=404, detail="Organizer not found to update")
        return data

    async def delete_organizer(self, organizer_id: str):
        await self.repo.init_db()
        deleted = await self.repo.delete(organizer_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Organizer not found to delete")

    async def events_managed_by_company(self, company: str) -> dict:
        await self.repo.init_db()
        total = await self.repo.events_managed_by_company(company)
        return {"company": company, "managed_events": total}

    async def region_with_max_cultural_events(self) -> dict:
        await self.repo.init_db()
        result = await self.repo.region_with_max_cultural_events()
        return result

    async def top_organizer_2025(self) -> Optional[Organizer]:
        await self.repo.init_db()
        return await self.repo.top_organizer_2025()

