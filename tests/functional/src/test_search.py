import json
import pytest
from settings import test_settings
from utils.redis_keys import Films


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'search': 'The Star', 'page': '1', 'page_size': '50'},
            {'status': 200, 'length': 30}
        ),
        (
            {'search': 'The Star', 'page': '1', 'page_size': '25'},
            {'status': 200, 'length': 25}
        ),
        (
            {'search': 'The Star', 'page': '3', 'page_size': '10'},
            {'status': 200, 'length': 10}
        ),
        (
            {'search': 'Mashed potato', 'page': '1', 'page_size': '50'},
            {'status': 200, 'length': 0}
        ),
        (
            {'search': 'The Star', 'page': '5', 'page_size': '50'},
            {'status': 200, 'length': 0}
        ),
        (
            {'search': 'Howard', 'page': '1', 'page_size': '50'},
            {'status': 200, 'length': 30}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(
    get_data_test,
    es_write_data,
    es_search_data,
    redis_get_key,
    api_get_query,
    query_data,
    expected_answer
):
    # 1. Получение данных для тестировани
    bulk_query = await get_data_test(
        file="testdata/data_movis.json",
        index=test_settings.es_index_movies,
        id=test_settings.es_id_field_movies
    )

    # 2. Загружаем данные в ES
    await es_write_data(
        _data=bulk_query,
        _index=test_settings.es_index_movies,
        _mapping=test_settings.es_index_mapping_movies
    )

    # 3. Поиск в ES
    search_data = await es_search_data(
        index=test_settings.es_index_movies,
        **query_data)

    # 4. Проверяем результат поиска в ES
    assert len(search_data) == expected_answer['length']

    # 5. Запрашиваем данные из ES по API
    body, headers, status = await api_get_query(
        url=f"{test_settings.service_url}/api/v1/films",
        query_data=query_data
    )

    # 6. Проверяем ответ
    assert status == expected_answer['status']
    assert len(body.get('movies')) == expected_answer['length']

    # 7. Запрашиваем данные из redis по выполненомы ранее запросу
    films = Films(**query_data)
    value = await redis_get_key(str(films))

    # 8. Сравнения результата из ES и Кэша
    assert body == json.loads(value)
