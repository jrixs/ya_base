
from elasticsearch import AsyncElasticsearch, NotFoundError
from settings import test_settings
import redis.asyncio as aioredis
import pytest_asyncio
import aiohttp
import asyncio
from elasticsearch.helpers import async_bulk
from utils.get_mappings import read_json_file


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', name='es_client')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host,
                                   verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope='session', name='es_write_data')
async def es_write_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        if await es_client.indices.exists(index=kwargs['_index']):
            await es_client.indices.delete(index=kwargs['_index'])
        await es_client.indices.create(index=kwargs['_index'],
                                       **kwargs['_mapping'])

        updated, errors = await async_bulk(
            client=es_client,
            actions=kwargs['_data'],
            refresh='wait_for')

        await es_client.close()

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture(scope='session', name='es_search_data')
async def es_search_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        try:
            doc = await es_client.search(
                index=kwargs['index'],
                body=kwargs['body'])
            return [hit["_source"] for hit in doc["hits"]["hits"]]
        except NotFoundError:
            return []

    yield inner


@pytest_asyncio.fixture(scope='session', name='es_get_data')
async def es_get_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        try:
            return await es_client.get(index=kwargs['index'], id=kwargs['id'])
        except NotFoundError:
            return []

    yield inner


@pytest_asyncio.fixture(scope='session', name='redis_client')
async def redis_client():
    redis_client = aioredis.Redis(host=test_settings.redis_host,
                                  port=test_settings.redis_port,
                                  decode_responses=True)
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(scope='session', name='redis_get_key')
async def redis_get_key(redis_client: aioredis.Redis):
    async def inner(key_name):
        return await redis_client.get(key_name)
    yield inner


@pytest_asyncio.fixture(scope='session', name='api_client')
async def api_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope='session', name='api_get_query')
async def api_get_query(api_client: aiohttp.ClientSession):
    async def inner(**kwargs):
        async with api_client.get(kwargs['url'],
                                  params=kwargs.get('query_data'),
                                  ssl=False) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status
    yield inner


@pytest_asyncio.fixture(scope='session', name='get_data_test')
async def get_data_test():
    async def inner(**kwargs):
        es_data = read_json_file(kwargs['file'])
        es_data = [hit['_source'] for hit in es_data['hits']['hits']]

        bulk_query: list[dict] = []
        for row in es_data:
            data = {'_index': kwargs['index'],
                    '_id': row[kwargs['id']]}
            data.update({'_source': row})
            bulk_query.append(data)

        return bulk_query

    yield inner
