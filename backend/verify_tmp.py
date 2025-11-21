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
    print('created type', type(created), 'data', created)
    events = await svc.get_all_events()
    ids = [e.id for e in events]
    print('events count', len(events), 'contains new?', created['id'] in ids)
    city = await svc.get_city_with_most_events()
    print('city stat', city)
    deleted = await svc.delete_event(created['id'])
    print('deleted result', deleted)

asyncio.run(main())
