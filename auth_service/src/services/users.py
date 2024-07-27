from core.connections import get_redis
from core.connections import get_session, SessionLocal
from redis.asyncio import Redis
from services.base_services import (
    BaseService, RedisStorage,
    PostgresDB, DB, Storage
    )
from schemas.user import UserData
from models.auth_data import User, History, Secret
from schemas.user import UserChange
from responses.user import UserResponse, UserHistoryResponse
from core.passwd import hash_password
from sqlalchemy import update

from fastapi import Depends


class GetUserInfo(BaseService):

    def __init__(self, db: DB, storage: Storage):
        super().__init__(db=db, storage=storage)

    def get_info(self, auth: UserData) -> UserResponse:
        user = self._db.session.query(User).filter(
            User.id == auth.id).first()
        return UserResponse(**user.__dict__)

    def get_history(self, auth: UserData, offset: int, limit: int
                    ) -> UserHistoryResponse:

        history = self._db.session.query(History).filter(
            History.user_id == auth.id).offset(offset).limit(limit).all()

        history = [{'last_logged_at': entry.last_logged_at,
                    'user_agent': entry.user_agent} for entry in history]

        return UserHistoryResponse(
            id=auth.id,
            history=history,
            total=len(history)
        )

    def put_user(self, auth: UserData, user_data: UserChange) -> bool:
        new_user_data = update(User).where(User.id == auth.id).values(
            username=user_data.username,
            email=user_data.email
            )

        new_user_secret = update(Secret).where(
            Secret.user_id == auth.id).values(
            password=hash_password(user_data.password)
            )

        return all([
            self._db.update(new_user_data),
            self._db.update(new_user_secret)
            ])


def get_user_info(
    redis: Redis = Depends(get_redis),
    session: SessionLocal = Depends(get_session),
) -> GetUserInfo:
    return GetUserInfo(db=PostgresDB(session),
                       storage=RedisStorage(redis))
