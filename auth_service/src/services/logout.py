from db.redis import get_redis
from db.postgres import get_session, SessionLocal
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )
from core.jwt import verify_token, get_secret_key

from fastapi import Depends


class BlockedToken(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def blocked(self, login: str,
                      access_token: str,
                      refresh_token: str) -> bool:

        secret_key = get_secret_key(login)
        if blocked_token(access_token, secret_key) and \
           blocked_token(refresh_token, secret_key):
            return True
        return False

    async def blocked_token(self, token, secret_key) -> bool:
        if not await self._storage.exists(token):
            if verify_token(token, secret_key) is not None:
                await self._storage.set(token, 'blocked')
                return True
        return False


def blocked_token(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> bool:
    return BlockedToken(db=PostgresDB(session),
                        storage=RedisStorage(redis))
