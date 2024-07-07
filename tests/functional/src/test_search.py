import uuid
import json
import pytest
from settings import test_settings
from utils.redis_keys import Films


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'search': 'The Star', 'page': '1', 'page_size': '50'},
            {'status': 200, 'length': 50}
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
            {'status': 200, 'length': 50}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(
    es_write_data,
    es_search_data,
    redis_get_key,
    api_get_query,
    query_data,
    expected_answer
):

    # 1. Генерируем данные для ES

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        "directors": [
            {"id": "efnnb8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Stan"}
        ],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ]
    } for _ in range(60)]

    # Формирование данных
    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': test_settings.es_index_movies,
                '_id': row[test_settings.es_id_field_movies]}
        data.update({'_source': row})
        bulk_query.append(data)

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

    # 8. Сравнения результата из ES и Кеша
    assert body == json.loads(value)
