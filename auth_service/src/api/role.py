from fastapi import APIRouter, status, Response

from src.schemas.role import RoleResponse, RoleRequest
from src.core.dependencies import PGService
from src.db import roles

router = APIRouter(prefix="/role")


@router.get("", status_code=status.HTTP_200_OK, response_model=list[RoleResponse])
async def get_all_roles(db_service: PGService) -> list[RoleResponse]:
    return await roles.get_all_roles(db_service)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoleResponse)
async def create_new_role(db_service: PGService, role_data: RoleRequest) -> RoleResponse:
    return await roles.add_new_role(db_service, role_data)


@router.put("/{role_id}", status_code=status.HTTP_200_OK, response_model=RoleResponse)
async def update_role(db_service: PGService, role_id: str, role_data: RoleRequest) -> RoleResponse:
    return await roles.update_role_parameters(db_service, role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_role(db_service: PGService, role_id: str) -> Response:
    await roles.delete_role(db_service, role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
