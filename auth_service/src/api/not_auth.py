from fastapi import APIRouter, status, Body, HTTPException, Depends, Response

from auth_service.src.schemas.login import LoginRequest

router = APIRouter()


@router.post("/login")
async def login_to_app(login_data: LoginRequest, response: Response):
    """хэшируется пароль из login_data по алгоритму и сравнивается с тем, что есть в бд.
    если всё ок, то возвращаются access, refresh токены, добавляются данные о входе
    если пароль неверен, то 401"""
    try:
        verify_user_password(login_data)
        access_token, refresh_token = create_tokens()
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        add_login_information()
        return response
    except IncorrectPasswordException:
        raise HTTPException()


@router.post("/register")
async def register_to_app(register_data: RegistrationRequest, response: Response) -> RegistrationResponse:
    """проверяем наличие юзера в базе. если юзер имеется - HTTP_400_BAD_REQUEST с указанием того, что юзернейм/имейл существуют.
    если юзера нет, производим регистрацию, назначаем базовую роль (её определит суперюзер), шифруем токены и даём ответ 200"""

