from fastapi import APIRouter, status, HTTPException, Depends
from services.logout import service_logout, BlockedToken

from core.dependencies import VerifiedUser

router = APIRouter()


@router.post("/logout",
             summary="logout",
             description="logout",
             )
async def logout(
    current_user: VerifiedUser,
    service_logout: BlockedToken = Depends(service_logout)
):
    """
    после получения данных по current_user - вычисляем время жизни у refresh и access токенов из их дешифровки и отправляем в redis с этим оставшимся временем жизни
    """

    if await service_logout.blocked(current_user):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Successful logout."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed logout."
        )
