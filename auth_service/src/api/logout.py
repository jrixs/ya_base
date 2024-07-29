from fastapi import APIRouter, status, Depends, Response, Request
from services.logout import service_logout, BlockedToken
from services.event import service_event, Event
from schemas.event import EventCreate

from core.dependencies import VerifiedUser

router = APIRouter()


@router.post("/logout",
             summary="logout",
             description="logout"
             )
async def logout(
    current_user: VerifiedUser,
    request: Request,
    response: Response,
    service_logout: BlockedToken = Depends(service_logout),
    add_login_information: Event = Depends(service_event)
):
    """
    после получения данных по current_user - вычисляем время жизни у refresh и
    access токенов из их дешифровки и отправляем в redis с этим оставшимся
    временем жизни
    """
    # Удаление cookies
    response.set_cookie(key="access", value='', httponly=True, max_age=0)
    response.set_cookie(key="refresh", value='', httponly=True, max_age=0)
    response.set_cookie(key="username", value='', httponly=True, max_age=0)

    # Блокироака ключей
    if await service_logout.blocked(current_user):

        # Запись события
        event = EventCreate(
            user_id=current_user.id,
            user_agent=f"logout.{request.headers.get('user-agent')}"
            )
        await add_login_information.set(event)

        return {"detail": "Successful logout."}
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Failed logout.")
