from fastapi import APIRouter, status, Body, HTTPException, Depends, Response

from schemas.role import RoleResponse,  RoleRequest

router = APIRouter(prefix="/role")


@router.get("", status_code=status.HTTP_200_OK, response_model=list[RoleResponse])
async def get_all_roles() -> list[RoleResponse]:
    pass


@router.post("", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_new_role(role_data: RoleRequest) -> Response:
    pass


@router.put("/{role_id}", status_code=status.HTTP_200_OK)
async def update_role(role_id: int, role_data: RoleRequest):
    pass


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role():
    pass

