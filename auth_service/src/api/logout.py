from fastapi import APIRouter, status, Depends, Response, Request
from fastapi.responses import JSONResponse
from services.logout import service_logout, BlockedToken
from services.event import service_event, Event
from schemas.event import EventCreate

from core.dependencies import VerifiedUser

router = APIRouter()


@router.post("/logout",
             summary="logout",
             description="logout",
             status_code=status.HTTP_200_OK,
             response_class=Response
             )
async def logout(
    current_user: VerifiedUser,
    request: Request,
    response: Response,
    service_logout: BlockedToken = Depends(service_logout),
    add_login_information: Event = Depends(service_event)
) -> Response:
    """
    после получения данных по current_user - вычисляем время жизни у refresh и
    access токенов из их дешифровки и отправляем в redis с этим оставшимся
    временем жизни
    """
    # Удаление cookies
    response.delete_cookie(key="access", httponly=True)
    response.delete_cookie(key="refresh", httponly=True)
    response.delete_cookie(key="username", httponly=True)

    # Блокироака ключей
    if await service_logout.blocked(current_user):

        # Запись события
        event = EventCreate(
            user_id=current_user.id,
            user_agent=f"logout.{request.headers.get('user-agent')}"
            )
        await add_login_information.set(event)

        return Response(status_code=status.HTTP_200_OK, content="Successful logout.")
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Failed logout.")
