from fastapi import APIRouter, status

from core.dependencies import PGService
from schemas.user import UserResponse
from db import users

router = APIRouter(prefix="/user")


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(db_service: PGService, user_id: str) -> UserResponse:
    return await users.get_one_user(db_service, user_id)


@router.put("/{user_id}/role/{role_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def set_user_role(db_service: PGService, user_id: str, role_id: str) -> UserResponse:
    return await users.update_user_role(db_service, user_uuid=user_id, role_uuid=role_id)
