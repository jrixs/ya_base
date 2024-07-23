from fastapi import APIRouter, status, Body, HTTPException, Depends, Response

from schemas.role import RoleResponse,  RoleRequest

router = APIRouter(prefix="/user")


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=list[RoleResponse])
async def get_user() -> list[RoleResponse]:
    pass


@router.put("/{user_id}/role/{role_id}", status_code=status.HTTP_200_OK)
async def set_user_role(role_id: int, role_data: RoleRequest):
    pass


@router.delete("/{user_id}/role/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unset_role_from_user():
    pass

