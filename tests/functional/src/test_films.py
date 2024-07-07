import json
import pytest
from settings import test_settings
from utils.redis_keys import Films
from elasticsearch import BadRequestError
from aiohttp import ClientSession
from utils.query_builder import query_builder_movies


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
            {"status": 422, "length": 30},
        ),
    ],
)
@pytest.mark.asyncio
async def test_films(
    get_data_test,
    es_write_data,
    es_search_data,
    redis_get_key,
    api_get_query,
    query_data,
    expected_answer,
):
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

    try:
        # 3. Поиск в ES
        search_data = await es_search_data(
            index=test_settings.es_index_movies,
            body=query_builder_movies(query_data)
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


# Эта штука заработает с норм data_movies
@pytest.mark.asyncio
async def test_film_details():
    async with ClientSession() as session:
        film_id = "d4b209dc-88fe-4380-a43e-8966673f2fe0"
        url = test_settings.service_url + f"/api/v1/films/{film_id}"
        status, body = await get_response(session, url)

        assert status == 200
        assert body["id"] == film_id
        assert body["imdb_rating"] == 7.6
        assert body["genres"] == ["Drama"]
        assert (
            body["title"]
            == "That movie is not Star wars. Episode VII. Last jedi"
        )
        assert (
            body["description"]
            == """
                Darth Vader travels in Austria.
                He flues on plane.
                He goes on Vienna's tram.
                All movie viewer looks all that looks Vader.
                And this movie is not Star wars. Episode VII. Last Jedi.
                """
        )
        assert body["directors_names"] == ["Marco Romano"]
        assert body["actors_names"] == []
        assert body["writers_names"] == ["Marco Romano"]
        assert body["directors"] == [
            {
                "id": "232fd5ab-166f-47e4-afe1-28d3450721d5",
                "name": "Marco Romano",
            }
        ]
        assert body["actors"] == []
        assert body["writers"] == [
            {
                "id": "232fd5ab-166f-47e4-afe1-28d3450721d5",
                "name": "Marco Romano",
            }
        ]


# Некорректный uuid
@pytest.mark.asyncio
async def test_invalid_uuid():
    async with ClientSession() as session:
        url = test_settings.service_url + "/api/v1/films/invalid_uuid"
        status, _ = await get_response(session, url)

        assert status == 404
