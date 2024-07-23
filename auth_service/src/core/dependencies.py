from typing import Annotated

from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from db.postgres import get_session
from db.redis import get_redis

from core.exception import (
    AccessTokenExpired,
    AccessTokenInvalid,
    RefreshTokenInvalid,
    AccessTokenBlocked
    )
from schemas.user import UserData
from core.jwt import (
    decode_token,
    verify_refresh_token,
    refresh_tokens,
    check_tokens_in_blocklist
    )


DBSession = Annotated[Session, Depends(get_session)]
RedisSession = Annotated[Redis, Depends(get_redis)]


def verify_user_access(
        request: Request,
        redis: RedisSession,
) -> UserData:
    access_token: str = request.cookies.get("access_token")
    refresh_token: str = request.cookies.get("refresh_token")
    username: str = request.cookies.get("username")

    try:
        """здесь добавить поход в редис и проверку на протухший токен, если протух, то 401"""
        check_tokens_in_blocklist(access_token, refresh_token, redis)
    except AccessTokenBlocked as err:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=err
            )

    try:
        """декодятся данные и заполняется объект userdata, при возникновении ошибок - выбрасываем исключения"""
        data: UserData = decode_token(access_token, username)
        data.access_token = access_token
        data.refresh_token = refresh_token
    except AccessTokenExpired:
        """если рефреш токен нормальный, то он пересоздает access token, убирается в редис и создается новый рефреш. 
        иначе выбрасываем исключение"""
        data: UserData = verify_refresh_token(refresh_token, username)
        new_access_token, new_refresh_token = refresh_tokens(data, redis)
        data.access_token = new_access_token
        data.refresh_token = new_refresh_token
    except (AccessTokenInvalid, RefreshTokenInvalid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return data


VerifiedUser = Annotated[UserData, Depends(verify_user_access)]


def verify_user_admin_rights(user_data: VerifiedUser) -> UserData:
    if user_data.is_superuser:
        return user_data
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied"
        )


VerifiedAdmin = Annotated[UserData, Depends(verify_user_admin_rights)]
