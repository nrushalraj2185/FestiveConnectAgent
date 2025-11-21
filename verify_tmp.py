import asyncio
from repos.repo import Repo
from services.service import Service
from models.data_models import Event
from constants import DB_NAME

async def main():
    repo = Repo(DB_NAME)
    svc = Service(repo)
    await repo.init_db()
    ev = Event(title='Test Verification Event', date='2025-12-25', location='Bangalore')
    created = await svc.create_event(ev)
    events = await svc.get_all_events()
    print('events count', len(events))
    city = await svc.get_city_with_most_events()
    print('city stat', city)
    await svc.delete_event(created['id'])

asyncio.run(main())
