from fastapi import APIRouter, Response, Depends, status, Request
from core.dependencies import VerifiedUser, HTTPException, PGService
from db import users, history

from schemas.user import UserResponse, UserHistoryResponse, BasePagination, UserCreate

router = APIRouter()


@router.get("/user", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def user_information(
        db_service: PGService,
        current_user: VerifiedUser,
) -> UserResponse:
    """Запрашиваем данные пользователя"""
    return await users.get_one_user(db_service, current_user.id)


@router.put("/user", status_code=status.HTTP_200_OK, response_class=Response)
async def update_user_information(
        db_service: PGService,
        current_user: VerifiedUser,
        request: Request,
        user_data: UserCreate,
) -> Response:
    """обновляем информацию о пользователе (имейл, пароль, юзернейм), после
    чего производим процесс шифрования пароля, инвалидации текущих токенов,
    выдачи новых токенов"""
    try:
        await users.update_user(db_service, current_user.id, user_data)
        await history.create_new_history_record(db_service, user_id=current_user.id,
                                                record_data=f"put.user.{request.headers.get('user-agent')}")
        return Response(status_code=status.HTTP_200_OK,
                        content="Successful change.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unsuccessful change.")


@router.get("/history", status_code=status.HTTP_200_OK, response_model=UserHistoryResponse)
async def get_user_history(
        db_service: PGService,
        current_user: VerifiedUser,
        pagination_options: BasePagination = Depends(),
) -> UserHistoryResponse:
    """Запрашиваем историю входов юзера с базовой настройкой
    пагинации limit/offset"""
    return await history.get_history_by_user(db_service, current_user.id, pagination_options)
