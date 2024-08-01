import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from core.passwd import hash_password
from models.auth_data import User
from models.auth_secret import Secret
from schemas.user import UserResponse, UserCreate
from services.base_services import PostgresDB


async def get_one_user(db_service: PostgresDB, user_uuid: str) -> UserResponse:
    statement = select(User).where(User.id == user_uuid)
    user_data = await db_service.select_one(statement)
    return UserResponse.model_validate(user_data)


async def get_one_user_by_username(db_service: PostgresDB, username: str) -> User:
    statement = select(User).where(User.username == username).options(joinedload(User.secret))
    return await db_service.select_one(statement)


async def update_user_role(db_service: PostgresDB, user_uuid: str, role_uuid: str) -> UserResponse:
    statement = update(User).where(User.id == user_uuid).values(role_id=role_uuid).returning(User)
    data = await db_service.update(statement)
    return UserResponse.model_validate(data)


async def update_user(db_service: PostgresDB, user_uuid: str, new_user_data: UserCreate):
    statement_user = update(User).where(User.id == user_uuid).values(username=new_user_data.username,
                                                                     email=new_user_data.email)
    statement_password = update(Secret).where(Secret.user_id == user_uuid).values(
        password=hash_password(new_user_data.password)
    )

    await db_service.update(statement_user)
    await db_service.update(statement_password)


async def check_user_exist_by_email(db_service: PostgresDB, user_email: str) -> bool:
    statement = select(User.id).where(User.email == user_email)
    return bool(await db_service.select_one(statement))


async def create_user(db_service: PostgresDB, user_data: UserCreate, role_id: str):
    user_id = str(uuid.uuid4())
    db_user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        role_id=role_id,
    )
    db_secret = Secret(
        id=str(uuid.uuid4()),
        user_id=user_id,
        password=hash_password(user_data.password)
    )

    new_user = await db_service.insert(db_user)
    await db_service.insert(db_secret)
    return new_user
