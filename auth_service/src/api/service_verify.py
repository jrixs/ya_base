from fastapi import APIRouter, status, HTTPException, Depends, Response, Body
from services.login import get_tokens, GetTokensService
from schemas.login import LoginRequest
from schemas.user import UserData
from core.exception import AuthenticationIncorrect

router = APIRouter(prefix="/service")


@router.post("/verify", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def verify_token_from_another_service(token: str = Body()) -> Response:
    """Верифицирует токен, отправленный на проверку от другого сервиса.
    При успехе отправляет пустой 204 ответ, при неуспехе 401 Unauthorized"""
    return Response(status_code=status.HTTP_204_NO_CONTENT)
