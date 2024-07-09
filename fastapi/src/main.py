from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from fastapi import FastAPI

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=settings.project_name,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    # Адрес документации в красивом интерфейсе
    docs_url="/api/openapi",
    # Адрес документации в формате OpenAPI
    openapi_url="/api/openapi.json",
    # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сериализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
)


@app.router.on_startup.append
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}{settings.elastic_host}:{settings.elastic_port}"
        ]
    )


@app.router.on_shutdown.append
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
