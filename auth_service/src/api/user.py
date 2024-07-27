from fastapi import APIRouter, Response, Depends, Query, status
from core.dependencies import VerifiedUser, HTTPException
from responses.user import UserResponse, UserHistoryResponse
from services.users import GetUserInfo, get_user_info
from schemas.user import UserChange

router = APIRouter()


@router.get("/user")
async def user_information(
    current_user: VerifiedUser,
    service_user: GetUserInfo = Depends(get_user_info)
) -> UserResponse:
    """запрашиваем данные пользователя"""
    return service_user.get_info(current_user)


@router.put("/user")
async def update_user_information(
    current_user: VerifiedUser,
    user_data: UserChange,
    service_user: GetUserInfo = Depends(get_user_info)
):
    """обновляем информацию о пользователе (имейл, пароль, юзернейм), после чего производим процесс шифрования пароля,
    инвалидации текущих токенов, выдачи новых токенов"""
    if service_user.put_user(current_user, user_data):
        return Response(status_code=status.HTTP_200_OK,
                        content="Successful change.")
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unsuccessful change.")


@router.get("/history")
async def get_user_history(
    current_user: VerifiedUser,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service_user: GetUserInfo = Depends(get_user_info)
) -> UserHistoryResponse:
    """запрашиваем историю входов юзера с базовой настройкой пагинации limit/offset"""
    return service_user.get_history(current_user, offset, limit)
