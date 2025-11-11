from typing import List
from fastapi import HTTPException
from models.data_models import Event
from repos.repo import Repo

class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    async def create_event(self, event: Event):
        await self.repo.init_db()
        if not event.id:
            from uuid import uuid4
            event.id = str(uuid4())
        existing = await self.repo.get(event.id)
        if existing:
            raise HTTPException(status_code=409, detail="Event already exists")
        await self.repo.insert(event)
        return event

    async def get_all_events(self) -> List[Event]:
        await self.repo.init_db()
        return await self.repo.list()

    async def get_event(self, event_id: str) -> Event:
        await self.repo.init_db()
        event = await self.repo.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    async def update_event(self, event_id: str, event: Event):
        await self.repo.init_db()
        event.id = event_id
        updated = await self.repo.update(event)
        if not updated:
            raise HTTPException(status_code=404, detail="Event not found to update")
        return event

    async def delete_event(self, event_id: str):
        await self.repo.init_db()
        deleted = await self.repo.delete(event_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Event not found to delete")
        # Return nothing; routers will set 204 No Content
        return
