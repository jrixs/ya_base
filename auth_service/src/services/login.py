from typing import Optional

from core.connections import get_redis
from core.connections import get_session, SessionLocal
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )

from schemas.user import UserData
from models.auth_data import User
from schemas.login import LoginRequest
from core.jwt import create_token, get_secret_key
from core.config import settings
from core.passwd import check_password
from core.exception import AuthenticationIncorrect

from fastapi import Depends


class GetTokensService(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def get(self, auth: LoginRequest) -> Optional[UserData]:
        # statement = select(User).where(User.username == auth.username)
        # user: User = self._db.select(statement)
        user = self._db.session.query(User).filter(
            User.username == auth.username).first()
        if user:
            if check_password(auth.password, user.secret.password):
                data = UserData(**user.__dict__)
                access_token = create_token(
                    payload=data.model_dump(),
                    secret_key=get_secret_key(data.username),
                    expires_in=settings.life_access_token
                    )
                refresh_token = create_token(
                    payload=data.model_dump(),
                    secret_key=get_secret_key(data.username),
                    expires_in=settings.life_refresh_token
                    )
                data.access_token = access_token
                data.refresh_token = refresh_token
                return data
        raise AuthenticationIncorrect


def get_tokens(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> GetTokensService:
    return GetTokensService(db=PostgresDB(session),
                            storage=RedisStorage(redis))
