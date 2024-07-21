from fastapi import APIRouter, status, Body, HTTPException, Depends
from services.logout import blocked_token

router = APIRouter()


@router.post("/",
             summary="logout",
             description="logout",
             )
async def logout(
    service_logout: bool = Depends(blocked_token),
    login: str = Body(..., embed=True),
    access_token: str = Body(..., embed=True),
    refresh_token: str = Body(..., embed=True)
):
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
