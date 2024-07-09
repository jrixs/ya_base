import json

import pytest
from aiohttp import ClientSession
from elasticsearch import BadRequestError

from settings import test_settings
from utils.query_builder import query_builder_movies
from utils.redis_keys import Films


@pytest.mark.asyncio
async def test_load_data(get_data_test, es_write_data):
    # 1. Получение данных для тестировани
    bulk_query = await get_data_test(
        file="testdata/data_movies.json",
        index=test_settings.es_index_movies,
        id=test_settings.es_id_field_movies,
    )

    # 2. Загружаем данные в ES
    await es_write_data(
        _data=bulk_query,
        _index=test_settings.es_index_movies,
        _mapping=test_settings.es_index_mapping_movies,
    )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {
                "order_by": "imdb_rating",
                "page": "1",
                "page_size": "10",
            },  # Сортировка
            {"status": 200, "length": 10},
        ),
        (
            {"page": "1", "page_size": "20"},  # Пагинация
            {"status": 200, "length": 20},
        ),
        (
            {"page": "50", "page_size": "50"},  # Страница где уже нет данных
            {"status": 200, "length": 0},
        ),
        (
            {"page": "1", "page_size": "-12"},  # Размер страницы меньше 1
            {"status": 422, "length": None},
        ),
        (
            {"page": "1", "page_size": "10"},  # Базовый запрос
            {"status": 200, "length": 10},
        ),
        (
            {"page": "-1", "page_size": "10"},  # Номер страницы отрицательный
            {"status": 422, "length": None},
        ),
        (
            {"page": "1", "page_size": "9999"},  # Размер страницы больше 100
            {"status": 422, "length": 20},
        ),
    ],
)
@pytest.mark.asyncio
async def test_films(
    es_search_data,
    redis_get_key,
    api_get_query,
    query_data,
    expected_answer,
):
    try:
        # 3. Поиск в ES
        search_data = await es_search_data(
            index=test_settings.es_index_movies,
            body=query_builder_movies(query_data),
        )

        # 4. Проверяем результат поиска в ES
        assert len(search_data) == expected_answer["length"]

    except BadRequestError:
        pass

    # 5. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/films", query_data=query_data
    )

    # 6. Проверяем ответ
    assert status == expected_answer["status"]
    if status == 200:
        assert len(body.get("movies")) == expected_answer["length"]

        # 7. Запрашиваем данные из redis по выполненному ранее запросу
        films = Films(**query_data)
        print(str(films))
        value = await redis_get_key(str(films))

        # 8. Сравнения результата из ES и Кеша
        assert body == json.loads(value)


@pytest.fixture
async def session():
    session = ClientSession()
    yield session
    await session.close()


async def get_response(session, url):
    async with session.get(url) as response:
        status = response.status
        body = await response.json()
        return status, body


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"id": "fc23ea9c-e799-419a-9df0-fc9d9b941a12"},
            {
                "imdb_rating": 4.7,
                "genres": ["Fantasy","Action","Adventure"],
                "status": 200,
                "data": True,
            },
        ),
        (
            {"id": "invalid_id"},
            {
                "imdb_rating": 0,
                "title": "",
                "genres": [],
                "status": 404,
                "data": False,
            },
        )
    ],
)
@pytest.mark.asyncio
async def test_film(
    es_get_data, redis_get_key, api_get_query, query_data, expected_answer
):

    # 1. Поиск в ES
    data = await es_get_data(
        index=test_settings.es_index_movies, **query_data
    )

    # 2. Проверяем результат из ES
    assert (len(data) > 0) == expected_answer["data"]
    if expected_answer["data"]:
        assert data["_source"]["imdb_rating"] == expected_answer["imdb_rating"]
        assert data["_source"]["genres"] == expected_answer["genres"]

    # 3. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/films/{query_data['id']}"
    )

    # 4. Проверяем ответ
    assert status == expected_answer["status"]
    if expected_answer["data"]:
        assert body["id"] == query_data["id"]
        assert body["imdb_rating"] == expected_answer["imdb_rating"]
        assert body["genres"] == expected_answer["genres"]

    # 5. Запрашиваем данные из redis по выполненомы ранее запросу
    value = await redis_get_key(f"film:{query_data['id']}")

    # 6. Сравнения результата из ES и Кэша
    if expected_answer["data"]:
        assert body == json.loads(value)
