from fastapi import APIRouter, status, Response, Request
from fastapi.responses import JSONResponse


from db.history import create_new_history_record
from services.logout import LogoutService

from core.dependencies import VerifiedUser, PGService

router = APIRouter()


@router.post("/logout", status_code=status.HTTP_200_OK, response_class=Response)
async def logout(
        db_service: PGService,
        current_user: VerifiedUser,
        request: Request,
        response: Response,
        service_logout: LogoutService,
) -> Response:
    """
    после получения данных по current_user - вычисляем время жизни у refresh и
    access токенов из их дешифровки и отправляем в redis с этим оставшимся
    временем жизни
    """

    # Блокироака ключей
    if await service_logout.blocked(current_user):
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successful logout."})

        # Удаление cookies
        response.delete_cookie(key="access", httponly=True)
        response.delete_cookie(key="refresh", httponly=True)
        response.delete_cookie(key="username", httponly=True)

        # Запись события
        await create_new_history_record(db_service, user_id=current_user.id,
                                        record_data=f"logout.{request.headers.get('user-agent')}")

        return response
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Failed logout."})
