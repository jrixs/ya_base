from core.dependencies import RedisSession, DBSession
from db.roles import get_one_role
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )
from schemas.user import UserData
from schemas.verify import VerifyToken
from core.jwt import verify_token, get_secret_key


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
        user_role = await get_one_role(self._db, user.role_id)
        return user_role.name == token.role_name


def get_verify(
        redis: RedisSession,
        session: DBSession,
) -> GetVerify:
    return GetVerify(db=PostgresDB(session),
                     storage=RedisStorage(redis))
