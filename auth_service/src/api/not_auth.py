from fastapi import APIRouter, status, HTTPException, Depends, Response
from services.login import get_tokens, GetTokensService
from schemas.login import LoginRequest
from schemas.user import UserData
from core.exception import AuthenticationIncorrect

router = APIRouter()


@router.post("/login")
async def login_to_app(
    login_data: LoginRequest,
    response: Response,
    service_login: GetTokensService = Depends(get_tokens)
):
    """хэшируется пароль из login_data по алгоритму и сравнивается с тем, что есть в бд.
    если всё ок, то возвращаются access, refresh токены, добавляются данные о входе
    если пароль неверен, то 401"""
    try:
        tokens: UserData = await service_login.get(login_data)
        response.set_cookie(key="access_token", value=tokens.access_token,
                            httponly=True)
        response.set_cookie(key="refresh_token", value=tokens.refresh_token,
                            httponly=True)
        # add_login_information()
        return response
    except AuthenticationIncorrect:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")


# @router.post("/register")
# async def register_to_app(register_data: RegistrationRequest, response: Response) -> RegistrationResponse:
#     """проверяем наличие юзера в базе. если юзер имеется - HTTP_400_BAD_REQUEST с указанием того, что юзернейм/имейл существуют.
#     если юзера нет, производим регистрацию, назначаем базовую роль (её определит суперюзер), шифруем токены и даём ответ 200"""

