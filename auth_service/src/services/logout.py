from db.redis import get_redis
from db.postgres import get_session, SessionLocal
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )
from schemas.user import UserData
from core.config import settings

from fastapi import Depends


class BlockedToken(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def blocked(self, user: UserData) -> bool:
        await self._storage.redis.set(user.access_token, user.username,
                                      settings.life_access_token)
        await self._storage.redis.set(user.refresh_token, user.username,
                                      settings.life_refresh_token)

        if self.blocked_token(user):
            return True
        return False

    async def blocked_token(self, user: UserData) -> bool:
        if await self._storage.get(user.access_token) and \
                await self._storage.get(user.refresh_token):
            return True
        return False


def service_logout(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> BlockedToken:
    return BlockedToken(db=PostgresDB(session),
                        storage=RedisStorage(redis))
