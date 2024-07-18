from api import test
from core.config import settings
from db import redis
from db.postgres import engine, create_database, purge_database
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from fastapi import FastAPI

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


@app.router.on_startup.append
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    from models.entity import User
    await create_database()
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await engine.connect()


@app.router.on_shutdown.append
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await purge_database()
    await engine.dispose()


app.include_router(test.router, prefix="/auth/test", tags=["test"])
