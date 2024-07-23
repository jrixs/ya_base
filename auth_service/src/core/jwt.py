import jwt
from typing import Dict, Tuple
from datetime import datetime, timedelta
from core.config import settings
from redis.asyncio import Redis
from schemas.user import UserData
from core.exception import (
    AccessTokenExpired,
    RefreshTokenInvalid,
    AccessTokenBlocked,
    RefreshTokenBlocked
    )
import logging

logger = logging.getLogger()


async def check_tokens_in_blocklist(
        access_token: str,
        refresh_token: str,
        redis: Redis
) -> None:
    if await redis.get(access_token):
        raise AccessTokenBlocked
    if await redis.get(refresh_token):
        raise RefreshTokenBlocked


async def refresh_tokens(
        refresh_token: str,
        user: UserData,
        redis: Redis
) -> Tuple[str, str]:
    await redis.set(refresh_token, user.username, settings.life_refresh_token)
    access_token = create_token(
        user.model_dump(),
        get_secret_key(user.username),
        settings.life_access_token)
    refresh_token = create_token(
        user.model_dump(),
        get_secret_key(user.username),
        settings.life_refresh_token)
    return access_token, refresh_token


def decode_token(access_token: str, username: str) -> UserData:
    data = verify_token(access_token, username)
    if data is None:
        raise AccessTokenExpired
    else:
        return UserData(**data)


def verify_refresh_token(refresh_token: str, username: str) -> UserData:
    data = verify_token(refresh_token, username)
    if data is None:
        raise RefreshTokenInvalid
    else:
        return UserData(**data)


def create_token(
        payload: Dict,
        secret_key: str,
        expires_in: int
) -> str:
    """Создает токен"""
    now = datetime.utcnow()
    exp = now + timedelta(seconds=expires_in)
    payload["iat"] = now
    payload["exp"] = exp
    return jwt.encode(payload, secret_key, algorithm='HS256')


def verify_token(token: str, secret_key: str) -> Dict | None:
    """Проверяет токен"""
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        # Проверяем время истечения
        if datetime.utcnow() >= datetime.fromtimestamp(decoded_token['exp']):
            return None  # Токен истек
        return decoded_token
    except jwt.exceptions.InvalidTokenError:
        return None


def get_secret_key(key):
    return f"{key}_Yandex" * 2
