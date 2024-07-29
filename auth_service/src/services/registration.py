from core.dependencies import RedisSession, DBSession
from core.exception import UserExistConflict, UserRolesAreNotCreated
from db import users, roles
from schemas.user import UserCreate

from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
)


class RegService(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def check_user(self, user: UserCreate):
        if await users.check_user_exist_by_email(self._db, user.email):
            raise UserExistConflict

    async def create_user(self, user: UserCreate):
        guest_role_id = await roles.get_guest_role_id(self._db)
        if not guest_role_id:
            raise UserRolesAreNotCreated

        db_user = await users.create_user(self._db, user, guest_role_id)

        return db_user


def registation_tokens(
        redis: RedisSession,
        session: DBSession,
) -> RegService:
    return RegService(db=PostgresDB(session),
                      storage=RedisStorage(redis))
