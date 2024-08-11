from fastapi import (APIRouter, status, HTTPException,
                     Depends, Response, Request)

from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError
from loguru import logger

from core.dependencies import PGService
from db.history import create_new_history_record
from services.login import get_tokens, GetTokensService
from schemas.login import LoginRequest
from schemas.user import UserData
from core.exception import AuthenticationIncorrect, UserExistConflict, UserRolesAreNotCreated
from schemas.user import UserCreate
from services.registration import RegService, registation_tokens
from core.config import settings
from core.yandex import ya_settings, redirect_uri
import httpx


router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK, response_class=Response)
async def login_to_app(
        db_service: PGService,
        login_data: LoginRequest,
        request: Request,
        response: Response,
        service_login: GetTokensService = Depends(get_tokens)
) -> Response:
    """хэшируется пароль из login_data по алгоритму и сравнивается с тем, что есть в бд.
    если всё ок, то возвращаются access, refresh токены, добавляются данные о входе
    если пароль неверен, то 401"""
    try:
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successful login"})
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

        await create_new_history_record(db_service, user_id=tokens.id,
                                        record_data=f"login.{request.headers.get('user-agent')}")
        return response
    except AuthenticationIncorrect:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid username or password"})


@router.post("/register", status_code=status.HTTP_200_OK, response_class=Response)
async def register_user(
        db_service: PGService,
        reg_data: UserCreate,
        request: Request,
        reg_service: RegService = Depends(registation_tokens),
) -> Response:
    try:
        user = UserCreate(username=reg_data.username,
                          email=reg_data.email, password=reg_data.password)
        await reg_service.check_user(user=user)
        registered = await reg_service.create_user(user=user)
        await create_new_history_record(db_service, user_id=registered.id,
                                        record_data=f"register.{request.headers.get('user-agent')}")
        return Response(status_code=status.HTTP_200_OK, content="Successful registration")
    except UserExistConflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist")
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    except (UserRolesAreNotCreated, Exception) as exc:
        logger.info(f"Exception: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration error")


@router.get("/yalogin")
async def login_via_yandex():
    # URL для авторизации через Яндекс
    auth_url = f"{ya_settings.YANDEX_AUTH_URL}?response_type=code&client_id={ya_settings.YANDEX_CLIENT_ID}&redirect_uri={redirect_uri}"
    return RedirectResponse(auth_url)

@router.get("/yalogin/callback")
async def yandex_callback(
    code: str,
    db_service: PGService,
    request: Request,
    response: Response,
    service_login: GetTokensService = Depends(get_tokens)
):
    """Обработка ответа от Яндекса после авторизации."""
    try:
        # Получение access token от Яндекса
        async with httpx.AsyncClient() as client:
            token_response = await client.post(ya_settings.YANDEX_TOKEN_URL, data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": ya_settings.YANDEX_CLIENT_ID,
                "client_secret": ya_settings.YANDEX_CLIENT_SECRET,
                "redirect_uri": "http://yourdomain.com/yalogin/callback"
            })
            token_data = token_response.json()

        if "access_token" not in token_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get access token from Yandex")

        access_token = token_data["access_token"]

        # Получение информации о пользователе
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(ya_settings.YANDEX_USERINFO_URL, headers={
                "Authorization": f"OAuth {access_token}"
            })
            userinfo = userinfo_response.json()

        email = userinfo.get("default_email")

        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided by Yandex")

        # Проверка, существует ли пользователь в базе данных
        tokens: UserData = await service_login.get_from_email(email)

        response.set_cookie(key="access", value=tokens.access_token,
                            httponly=True, expires=settings.life_access_token
                            )
        response.set_cookie(key="refresh", value=tokens.refresh_token,
                            httponly=True, expires=settings.life_refresh_token
                            )
        response.set_cookie(key="username", value=tokens.username,
                            httponly=True, expires=settings.life_refresh_token
                            )

        await create_new_history_record(db_service, user_id=tokens.id,
                                        record_data=f"yalogin.{request.headers.get('user-agent')}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successful login via Yandex"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Yandex authentication failed or user not found"}
        )
