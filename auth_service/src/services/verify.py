from core.connections import get_redis
from core.connections import get_session, SessionLocal
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )
from schemas.user import UserData
from schemas.verify import VerifyToken
from core.jwt import verify_token, get_secret_key
from fastapi import Depends
from models.auth_service import Role


class GetVerify(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def check(self, token: VerifyToken):
        # Проверка токена в blacklist
        if await self._storage.get(token.access_token):
            return False

        # Проверка валидации jwt токена
        data = verify_token(token.access_token, get_secret_key(token.username))
        if data is None:
            return False

        # Получение роли
        user = UserData(**data)
        user_role = self._db.session.query(Role).filter(
            Role.id == user.role_id).one_or_none()
        return user_role.name == token.role_name


def get_verify(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> GetVerify:
    return GetVerify(db=PostgresDB(session),
                     storage=RedisStorage(redis))
