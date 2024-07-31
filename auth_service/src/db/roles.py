import uuid

from sqlalchemy import select, delete, update

from schemas.role import RoleResponse, RoleRequest
from services.base_services import PostgresDB
from models.auth_service import Role


async def get_one_role(db_service: PostgresDB, uuid: str) -> RoleResponse:
    statement = select(Role).where(Role.id == uuid)
    data = db_service.select_one(statement)
    return RoleResponse.model_validate(data)


async def get_all_roles(db_service: PostgresDB) -> list[RoleResponse]:
    statement = select(Role)
    data = db_service.select_few(statement)
    return [RoleResponse.model_validate(item) for item in data]


async def get_guest_role_id(db_service: PostgresDB) -> str:
    statement = select(Role.id).where(Role.name == "guest")
    role_id = db_service.select_one(statement)
    return role_id


async def add_new_role(db_service: PostgresDB, role_data: RoleRequest) -> RoleResponse:
    new_role = Role(**role_data.model_dump())
    new_role.id = uuid.uuid4()
    created_role = db_service.insert(new_role)
    return RoleResponse.model_validate(created_role)


async def update_role_parameters(db_service: PostgresDB, uuid: str, role_data: RoleRequest):
    statement = update(Role).where(Role.id == uuid).values(
        name=role_data.name,
        create_access=role_data.create_access,
        update_access=role_data.update_access,
        view_access=role_data.view_access,
        delete_access=role_data.delete_access
    ).returning(Role)
    db_service.update(statement)


async def delete_role(db_service: PostgresDB, uuid: str):
    statement = delete(Role).where(Role.id == uuid)
    db_service.delete(statement)
