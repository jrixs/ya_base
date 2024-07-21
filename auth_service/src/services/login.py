from typing import Optional

from db.redis import get_redis
from db.postgres import get_session, SessionLocal
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )

from schemas.login import TokensService
from models.auth_data import User
from core.jwt import create_token, get_secret_key
from core.passwd import check_password

from fastapi import Depends


class GetTokensService(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def get(self, login: str, password: str) -> Optional[TokensService]:
        user = self._db.query(obj=User, filter={'username': login})
        if user:
            if check_password(password, user.secret.password):
                access_token = create_token(
                    payload={
                        "id": user.id,
                        "role": user.role,
                        "is_superuser": user.is_superuser},
                    secret_key=get_secret_key(login),
                    expires_in=60 * 60
                    )
                refresh_token = create_token(payload={
                        "id": user.id,
                        "role": user.role,
                        "is_superuser": user.is_superuser},
                    secret_key=get_secret_key(login),
                    expires_in=60 * 60 * 24 * 7
                    )
                tokens = TokensService(**user.as_dict())
                tokens.access_token = access_token
                tokens.refresh_token = refresh_token
                return tokens
            return None
        return None


def get_tokens(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> TokensService:
    return GetTokensService(db=PostgresDB(session),
                            storage=RedisStorage(redis))
