import json
import pytest
from settings import test_settings
from utils.redis_keys import Genres
from utils.query_builder import query_builder_genres
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_load_data(get_data_test, es_write_data):
    # 1. Получение данных для тестировани
    bulk_query = await get_data_test(
        file="testdata/data_genres.json",
        index=test_settings.es_index_genres,
        id=test_settings.es_id_field_genres,
    )

    # 2. Загружаем данные в ES
    await es_write_data(
        _data=bulk_query,
        _index=test_settings.es_index_genres,
        _mapping=test_settings.es_index_mapping_genres,
    )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"genre_name": "War"}, {"status": HTTPStatus.OK, "length": 1}),
        ({"genre_name": "Music"}, {"status": HTTPStatus.OK, "length": 1}),
        ({"genre_name": "Nikas"}, {"status": HTTPStatus.OK, "length": 0}),
        ({"genre_name": "aaa"}, {"status": HTTPStatus.OK, "length": 0}),
        ({"genre_name": ""}, {"status": HTTPStatus.OK, "length": 21}),
    ],
)
async def test_genres(
    es_search_data, redis_get_key, api_get_query, query_data, expected_answer
):

    # 1. Поиск в ES
    search_data = await es_search_data(
        index=test_settings.es_index_genres,
        body=query_builder_genres(query_data),
    )

    # 2. Проверяем результат поиска в ES
    assert len(search_data) == expected_answer["length"]

    # 3. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/genres", query_data=query_data
    )

    # 4. Проверяем ответ
    assert status == expected_answer["status"]
    assert len(body.get("genres")) == expected_answer["length"]

    # 5. Запрашиваем данные из redis по выполненному ранее запросу
    genres = Genres(**query_data)
    value = await redis_get_key(str(genres))

    if len(search_data) > 0:
        # 6. Сравнения результата из ES и Кэша
        assert body == json.loads(value)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"id": "c020dab2-e9bd-4758-95ca-dbe363462173"},
            {"genre": "War", "films": 12, "status": HTTPStatus.OK, "data": True},
        ),
        (
            {"id": "eb7212a7-dd10-4552-bf7b-7a505a8c0b95"},
            {"genre": "History", "films": 20, "status": HTTPStatus.OK, "data": True},
        ),
        (
            {"id": "eb7212a7-dd10-4552-bf7b-7a505a8c0b95sss"},
            {"genre": "", "films": 0, "status": HTTPStatus.NOT_FOUND, "data": False},
        ),
        (
            {"id": "id/eb7212a7-dd10-4552-bf7b-7a505a8c0b95"},
            {"genre": "", "films": 0, "status": HTTPStatus.NOT_FOUND, "data": False},
        ),
        (
            {"id": "a886d0ec-c3f3-4b16-b973-dedcf5bfa395"},
            {"genre": "Short", "films": 172, "status": HTTPStatus.OK, "data": True},
        ),
    ],
)
async def test_genre(
    es_get_data, redis_get_key, api_get_query, query_data, expected_answer
):

    # 1. Поиск в ES
    data = await es_get_data(index=test_settings.es_index_genres, **query_data)

    # 2. Проверяем результат из ES
    assert (len(data) > 0) == expected_answer["data"]
    if expected_answer["data"]:
        assert data["_source"]["genre"] == expected_answer["genre"]
        assert len(data["_source"]["films"]) == expected_answer["films"]

    # 3. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/genres/{query_data['id']}"
    )

    # 4. Проверяем ответ
    assert status == expected_answer["status"]
    if expected_answer["data"]:
        assert body["id"] == query_data["id"]
        assert body["genre"] == expected_answer["genre"]
        assert len(body["films"]) == expected_answer["films"]

    # 5. Запрашиваем данные из redis по выполненомы ранее запросу
    value = await redis_get_key(f"genre:{query_data['id']}")

    # 6. Сравнения результата из ES и Кэша
    if expected_answer["data"]:
        assert body == json.loads(value)
