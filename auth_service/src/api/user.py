from fastapi import APIRouter, Response

from auth_service.src.core.dependencies import VerifiedUser
from auth_service.src.schemas.user import UserHistoryResponse, BasePagination

router = APIRouter(prefix="/user")


@router.get("/{user_id}/history")
async def get_user_history(current_user: VerifiedUser, request_options: BasePagination) -> UserHistoryResponse:
    """запрашиваем историю входов юзера с базовой настройкой пагинации limit/offset"""


@router.put("/{user_id}")
async def update_user_information(current_user: VerifiedUser, response: Response):
    """обновляем информацию о пользователе (имейл, пароль, юзернейм), после чего производим процесс шифрования пароля,
    инвалидации текущих токенов, выдачи новых токенов"""