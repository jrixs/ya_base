from fastapi import APIRouter, status, HTTPException, Depends, Response, Form
from services.login import get_tokens, GetTokensService
from schemas.login import LoginRequest
from schemas.user import UserData
from core.exception import AuthenticationIncorrect
from db.postgres import get_session
from schemas.user import UserCreate, UserResponse
from services.registration import RegService, registation_tokens
from pydantic import ValidationError

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

@router.post("/register")
async def register_user(
    username: str = Form(..., description="username of the user"),
    email: str = Form(..., description="Email address of the user"),
    password: str = Form(..., description="Password for the user"),
    reg_service: RegService = Depends(registation_tokens)
    ):
    try:
        user = UserCreate(username=username, email=email, password=password)
    except ValidationError:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email")
    exist_user = await reg_service.check_user(user=user)
    if exist_user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User_already_exist")
    
    registered = await reg_service.create_user(user=user)
    if registered:
        return Response(status_code=200)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="registration error")