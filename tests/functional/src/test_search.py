import uuid
import time
import json

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import test_settings
from utils.redis_keys import Films
import conftest


@pytest.mark.asyncio
async def test_search():

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
        data = {'_index': test_settings.es_index_movies, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    # 2. Загружаем данные в ES

    es_client: AsyncElasticsearch = await conftest.es_client()
    if await es_client.indices.exists(index=test_settings.es_index_movies):
        await es_client.indices.delete(index=test_settings.es_index_movies)
    await es_client.indices.create(index=test_settings.es_index_movies,
                                   **test_settings.es_index_mapping_movies)

    updated, errors = await async_bulk(client=es_client, actions=bulk_query)

    await es_client.close()

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    # Время для обновления индекса ES
    time.sleep(3)

    # 3. Запрашиваем данные из ES по API

    session = aiohttp.ClientSession()
    url = test_settings.service_url + '/api/v1/films'
    query_data = {'search': 'The Star', 'page': '1', 'page_size': '50'}
    async with session.get(url, params=query_data, ssl=False) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    await session.close()

    # 4. Проверяем ответ
    assert status == 200
    assert len(body.get('movies')) == 50

    # 5. Запрашиваем данные из redis по выполненомы ранее запросу
    films = Films(**query_data)
    value = await conftest.redis_get_key(str(films))

    # 6. Сравнения результата из ES и Кеша
    assert body == json.loads(value)
