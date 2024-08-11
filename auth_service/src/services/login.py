from typing import Optional

from core.dependencies import RedisSession, DBSession
from db import users
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
)

from schemas.user import UserData
from schemas.login import LoginRequest
from core.jwt import create_token, get_secret_key
from core.config import settings
from core.passwd import check_password
from core.exception import AuthenticationIncorrect


class GetTokensService(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def get(self, auth: LoginRequest) -> Optional[UserData]:
        user = await users.get_one_user_by_username(self._db, auth.username)
        if user:
            if check_password(auth.password, user.secret.password):
                data = UserData.model_validate(user)
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
    
    async def get_from_email(self, auth: LoginRequest) -> Optional[UserData]:
        user = await users.get_one_user_by_email(self._db, auth.username)
        if user:
            data = UserData.model_validate(user)
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
        redis: RedisSession,
        session: DBSession,
) -> GetTokensService:
    return GetTokensService(db=PostgresDB(session),
                            storage=RedisStorage(redis))
