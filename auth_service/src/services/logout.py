from typing import Annotated

from fastapi import Depends

from core.dependencies import RedisSession, DBSession
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
)
from schemas.user import UserData
from core.config import settings


class BlockedToken(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def blocked(self, user: UserData) -> bool:
        await self._storage.set(user.access_token, user.username,
                                settings.life_access_token)
        await self._storage.set(user.refresh_token, user.username,
                                settings.life_refresh_token)

        if await self.blocked_token(user):
            return True
        return False

    async def blocked_token(self, user: UserData) -> bool:
        if await self._storage.get(user.access_token) and \
                await self._storage.get(user.refresh_token):
            return True
        return False


def service_logout(
        redis: RedisSession,
        session: DBSession,
) -> BlockedToken:
    return BlockedToken(db=PostgresDB(session),
                        storage=RedisStorage(redis))


LogoutService = Annotated[BlockedToken, Depends(service_logout)]
