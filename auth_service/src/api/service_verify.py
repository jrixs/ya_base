from fastapi import APIRouter, status, Depends, Response, Body
from services.verify import get_verify, GetVerify
from schemas.verify import VerifyToken

router = APIRouter()


@router.post("/verify", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def verify_token_from_another_service(
    token: VerifyToken,
    service_user: GetVerify = Depends(get_verify)
) -> Response:
    """Верифицирует токен, отправленный на проверку от другого сервиса.
    При успехе отправляет пустой 204 ответ, при неуспехе 401 Unauthorized"""
    if await service_user.check(token):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
