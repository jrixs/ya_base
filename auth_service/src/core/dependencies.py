from typing import Annotated

from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from core.connections import get_session
from core.connections import get_redis
from loguru import logger

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
    check_tokens_in_blocklist,
    get_secret_key
    )

from services.base_services import PostgresDB

DBSession = Annotated[AsyncSession, Depends(get_session)]
RedisSession = Annotated[Redis, Depends(get_redis)]


def init_postgres_service(db_session: DBSession) -> PostgresDB:
    try:
        return PostgresDB(db_session)
    except Exception:
        logger.warning("Postgres Service was not initialized")


PGService = Annotated[PostgresDB, Depends(init_postgres_service)]


async def verify_user_access(
        request: Request,
        redis: RedisSession,
) -> UserData:
    access_token: str = request.cookies.get("access")
    refresh_token: str = request.cookies.get("refresh")
    username: str = request.cookies.get("username")

    try:
        """здесь добавить поход в редис и проверку на протухший токен, если протух, то 401"""
        await check_tokens_in_blocklist(access_token, refresh_token, redis)
    except (AccessTokenBlocked, Exception) as err:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err)
            )

    try:
        """декодятся данные и заполняется объект userdata, при возникновении ошибок - выбрасываем исключения"""
        data: UserData = decode_token(access_token, get_secret_key(username))
        data.access_token = access_token
        data.refresh_token = refresh_token
    except AccessTokenExpired:
        """если рефреш токен нормальный, то он пересоздает access token, убирается в редис и создается новый рефреш. 
        иначе выбрасываем исключение"""
        try:
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


async def verify_user_admin_rights(user_data: VerifiedUser) -> UserData:
    if user_data.is_superuser:
        return user_data
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied"
        )


VerifiedAdmin = Annotated[UserData, Depends(verify_user_admin_rights)]
