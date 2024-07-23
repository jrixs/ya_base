from fastapi import APIRouter, status, Body, HTTPException, Depends
from services.logout import blocked_token

from auth_service.src.core.dependencies import VerifiedUser

router = APIRouter()


@router.post("/logout",
             summary="logout",
             description="logout",
             )
async def logout(
    current_user: VerifiedUser
):
    """
    после получения данных по current_user - вычисляем время жизни у refresh и access токенов из их дешифровки и отправляем в redis с этим оставшимся временем жизни
    """

    blocked = await service_logout.blocked(
        login=login,
        access_token=access_token,
        refresh_token=refresh_token
        )
    if blocked:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Successful logout."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed logout."
        )
