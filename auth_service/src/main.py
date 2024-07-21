from contextlib import asynccontextmanager
import logging

from api import test, login, logout
from core.config import settings
from db import redis
from db.postgres import engine
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from api.registration import router as registration_router

from fastapi import FastAPI

from models.auth_service import Role

logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    engine.connect()
    yield
    await redis.redis.close()
    engine.dispose()
    

app = FastAPI(
    # Конфигурируем название проекта.
    title=settings.project_name,
    # Описание проекта.
    description="Это API для регистрации и аутентификации пользователей с использованием токенов JWT.",
    # Адрес документации в красивом интерфейсе
    docs_url="/auth/openapi",
    # Адрес документации в формате OpenAPI
    openapi_url="/auth/openapi.json",
    # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сериализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
)

app.include_router(test.router, prefix="/auth/test", tags=["test"])
app.include_router(registration_router, prefix="/auth", tags=["registration"])
app.include_router(logout.router, prefix="/auth/logout", tags=["logout"])

