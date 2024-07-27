from sqlalchemy import select, update

from models.auth_data import User
from schemas.user import UserResponse
from services.base_services import PostgresDB


async def get_one_user(db_service: PostgresDB, user_uuid: str) -> UserResponse:
    statement = select(User).where(User.id == user_uuid)
    user_data = db_service.select(statement)
    return UserResponse.model_validate(user_data)


async def update_user_role(db_service: PostgresDB, user_uuid: str, role_uuid: str) -> UserResponse:
    statement = update(User).where(User.id == user_uuid).values(role_id=role_uuid).returning(User)
    data = db_service.update(statement)
    return UserResponse.model_validate(data)
