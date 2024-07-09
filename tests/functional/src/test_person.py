import json

import pytest

from settings import test_settings
from utils.query_builder import query_builder_persons
from utils.redis_keys import Persons


@pytest.mark.asyncio
async def test_load_data(
    get_data_test,
    es_write_data
):
    # 1. Получение данных для тестировани
    bulk_query = await get_data_test(
        file="testdata/data_person.json",
        index=test_settings.es_index_persons,
        id=test_settings.es_id_field_persons
    )

    # 2. Загружаем данные в ES
    await es_write_data(
        _data=bulk_query,
        _index=test_settings.es_index_persons,
        _mapping=test_settings.es_index_mapping_persons
    )


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'name': 'Franklin Killian', 'page': '1', 'page_size': '10'},
            {'status': 200, 'length': 1}
        ),
        (
            {'name': 'James Ohlen', 'page': '1', 'page_size': '10'},
            {'status': 200, 'length': 1}
        ),
        (
            {'name': 'Yuri Synovets', 'page': '1', 'page_size': '10'},
            {'status': 200, 'length': 0}
        ),
        (
            {'name': '', 'page': '10', 'page_size': '10'},
            {'status': 200, 'length': 10}
        ),
        (
            {'name': '', 'page': '1', 'page_size': '100'},
            {'status': 200, 'length': 100}
        ),
        (
            {'name': '', 'page': '100', 'page_size': '100'},
            {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_persons(
    es_search_data,
    redis_get_key,
    api_get_query,
    query_data,
    expected_answer
):

    # 1. Поиск в ES
    search_data = await es_search_data(
        index=test_settings.es_index_persons,
        body=query_builder_persons(query_data))

    # 2. Проверяем результат поиска в ES
    assert len(search_data) == expected_answer['length']

    # 3. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/persons",
        query_data=query_data
    )

    # 4. Проверяем ответ
    assert status == expected_answer['status']
    assert len(body.get('persons')) == expected_answer['length']

    # 5. Запрашиваем данные из redis по выполненомы ранее запросу
    films = Persons(**query_data)
    value = await redis_get_key(str(films))

    # 6. Сравнения результата из ES и Кэша
    assert body == json.loads(value)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': '61bffbdc-910e-47b9-8b04-43b5f27807b4'},
            {'full_name': 'James Ohlen', 'films': 4, 'status': 200,
             'data': True}
        ),
        (
            {'id': '535fbcb6-2768-42c2-a3ab-878c7b2c42ab'},
            {'full_name': 'Trevor Devall', 'films': 7, 'status': 200,
             'data': True}
        ),
        (
            {'id': '535fbcb6-2768-42c2-a3ab-878c7b2c42a1'},
            {'full_name': '', 'films': 0, 'status': 404,
             'data': False}
        ),
        (
            {'id': 'id/535fbcb6-2768-42c2-a3ab-878c7b2c42a1'},
            {'full_name': '', 'films': 0, 'status': 404,
             'data': False}
        ),
        (
            {'id': 'e5edfe19-862a-4a23-9eb1-73f26ee7598a'},
            {'full_name': 'William McNamara', 'films': 2, 'status': 200,
             'data': True}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person(
    es_get_data,
    redis_get_key,
    api_get_query,
    query_data,
    expected_answer
):

    # 1. Поиск в ES
    data = await es_get_data(
        index=test_settings.es_index_persons,
        **query_data)

    # 2. Проверяем результат из ES
    assert (len(data) > 0) == expected_answer['data']
    if expected_answer['data']:
        assert data['_source']['full_name'] == expected_answer['full_name']
        assert len(data['_source']['films']) == expected_answer['films']

    # 3. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/persons/{query_data['id']}"
    )

    # 4. Проверяем ответ
    assert status == expected_answer['status']
    if expected_answer['data']:
        assert body['id'] == query_data['id']
        assert body['full_name'] == expected_answer['full_name']
        assert len(body['films']) == expected_answer['films']

    # 5. Запрашиваем данные из redis по выполненомы ранее запросу
    value = await redis_get_key(f"person:{query_data['id']}")

    # 6. Сравнения результата из ES и Кэша
    if expected_answer['data']:
        assert body == json.loads(value)
