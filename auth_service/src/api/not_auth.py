from fastapi import (APIRouter, status, HTTPException,
                     Depends, Response, Request, Form)
from services.login import get_tokens, GetTokensService
from services.event import service_event, Event
from schemas.login import LoginRequest
from schemas.user import UserData
from core.exception import AuthenticationIncorrect
from schemas.user import UserCreate
from services.registration import RegService, registation_tokens
from core.config import settings
from schemas.event import EventCreate
from pydantic import ValidationError

router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK, response_class=Response)
async def login_to_app(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    service_login: GetTokensService = Depends(get_tokens),
    add_login_information: Event = Depends(service_event)
) -> Response:
    """хэшируется пароль из login_data по алгоритму и сравнивается с тем, что есть в бд.
    если всё ок, то возвращаются access, refresh токены, добавляются данные о входе
    если пароль неверен, то 401"""
    try:
        tokens: UserData = await service_login.get(login_data)
        response.set_cookie(key="access", value=tokens.access_token,
                            httponly=True, expires=settings.life_access_token
                            )
        response.set_cookie(key="refresh", value=tokens.refresh_token,
                            httponly=True, expires=settings.life_refresh_token
                            )
        response.set_cookie(key="username", value=tokens.username,
                            httponly=True, expires=settings.life_refresh_token
                            )
        event = EventCreate(
            user_id=tokens.id,
            user_agent=f"login.{request.headers.get('user-agent')}"
            )
        await add_login_information.set(event)
        return Response(status_code=status.HTTP_200_OK, content="Successful login")
    except AuthenticationIncorrect:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")


@router.post("/register", status_code=status.HTTP_200_OK, response_class=Response)
async def register_user(
    reg_data: UserCreate,
    request: Request,
    reg_service: RegService = Depends(registation_tokens),
    add_login_information: Event = Depends(service_event)
) -> Response:
    try:
        user = UserCreate(username=reg_data.username, 
                          email=reg_data.email, password=reg_data.password)
    except ValidationError:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email")
    exist_user = await reg_service.check_user(user=user)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User_already_exist")

    registered = await reg_service.create_user(user=user)
    if registered:
        event = EventCreate(
            user_id=registered.id,
            user_agent=f"register.{request.headers.get('user-agent')}"
            )
        await add_login_information.set(event)
        return Response(status_code=status.HTTP_200_OK, content="Successful registration")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="registration error")
