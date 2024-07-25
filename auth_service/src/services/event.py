from db.redis import get_redis
from db.postgres import get_session, SessionLocal
from models.auth_data import History
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )
from schemas.event import EventCreate
from core.config import settings
from typing import List
import uuid
from uuid import UUID
from datetime import datetime

from fastapi import Depends


class Event(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def set(self, event: EventCreate) -> None:
        db_event = History(
            id=str(uuid.uuid4()),
            user_id=event.user_id,
            last_logged_at=datetime.now(),
            user_agent=event.user_agent
        )
        self._db.insert(db_event)

    async def get(self, user_id: UUID) -> List:
        pass


def service_event(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> Event:
    return Event(db=PostgresDB(session),
                 storage=RedisStorage(redis))
