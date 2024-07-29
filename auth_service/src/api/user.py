from fastapi import APIRouter, Response, Depends, status, Request
from core.dependencies import VerifiedUser, HTTPException
from responses.user import UserResponse, UserHistoryResponse
from services.users import GetUserInfo, get_user_info
from services.event import service_event, Event
from schemas.event import EventCreate
from schemas.user import UserChange

from schemas.user import BasePagination

router = APIRouter()


@router.get("/user", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def user_information(
    current_user: VerifiedUser,
    service_user: GetUserInfo = Depends(get_user_info)
) -> UserResponse:
    """запрашиваем данные пользователя"""
    return service_user.get_info(current_user)


@router.put("/user", status_code=status.HTTP_200_OK, response_class=Response)
async def update_user_information(
    current_user: VerifiedUser,
    request: Request,
    user_data: UserChange,
    service_user: GetUserInfo = Depends(get_user_info),
    add_login_information: Event = Depends(service_event)
) -> Response:
    """обновляем информацию о пользователе (имейл, пароль, юзернейм), после
    чего производим процесс шифрования пароля, инвалидации текущих токенов,
    выдачи новых токенов"""
    if service_user.put_user(current_user, user_data):
        # Запись события
        event = EventCreate(
            user_id=current_user.id,
            user_agent=f"put.user.{request.headers.get('user-agent')}"
            )
        await add_login_information.set(event)
        return Response(status_code=status.HTTP_200_OK,
                        content="Successful change.")
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unsuccessful change.")


@router.get("/history", status_code=status.HTTP_200_OK, response_model=UserHistoryResponse)
async def get_user_history(
    current_user: VerifiedUser,
    pagination_options: BasePagination = Depends(),
    service_user: GetUserInfo = Depends(get_user_info)
) -> UserHistoryResponse:
    """запрашиваем историю входов юзера с базовой настройкой
    пагинации limit/offset"""
    return service_user.get_history(current_user, pagination_options.offset, pagination_options.limit)
