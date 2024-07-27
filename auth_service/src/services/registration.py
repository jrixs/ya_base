from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.auth_data import User
from models.auth_secret import Secret
from models.auth_service import Role
from core.passwd import hash_password
from schemas.user import UserCreate
import uuid
from sqlalchemy.future import select
from datetime import datetime

from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )

from core.connections import get_redis
from core.connections import get_session, SessionLocal
from redis.asyncio import Redis


class RegService(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    async def check_user(self, user: UserCreate):
        existing_user = self._db.session.query(
            User).filter(User.email == user.email).first()
        if existing_user:
            return True
        return False

    async def create_user(self, user: UserCreate):

        role_id = "16191190-3781-4f94-8d66-92c2bcef7fea"
        existing_role = self._db.session.query(
            Role).filter(Role.id == role_id).first()

        if not existing_role:
            role = Role(
                id=role_id,
                name="test_role",
                user=[]
                )
            self._db.insert(role)

        hashed_password = hash_password(user.password)
        db_user = User(
            id=str(uuid.uuid4()),
            username=user.username,
            email=user.email,
            role_id=role_id,
            is_superuser=False,
            joined_at=str(datetime.now()),
            updated_at=str(datetime.now())
        )

        self._db.insert(db_user)

        db_secret = Secret(
            id=str(uuid.uuid4()),
            user_id=db_user.id,
            password=hashed_password,
            updated_at=str(datetime.now())
        )
        self._db.insert(db_secret)
        return db_user


def registation_tokens(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> RegService:
    return RegService(db=PostgresDB(session),
                            storage=RedisStorage(redis))
