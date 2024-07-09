
import asyncio

import aiohttp
import backoff
import pytest_asyncio
import redis.asyncio as aioredis
from elasticsearch import (AsyncElasticsearch, ConnectionError, NotFoundError,
                           TransportError)
from elasticsearch.helpers import async_bulk

from settings import test_settings
from utils.get_mappings import read_json_file


@pytest_asyncio.fixture(scope='session')
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def backoff_handler(awaitable, *args, **kwargs):
    @backoff.on_exception(backoff.expo,
                          (ConnectionError, TransportError,
                           aiohttp.ClientError, aioredis.RedisError),
                          max_tries=8,
                          max_time=60)
    async def wrapper():
        return await awaitable(*args, **kwargs)
    return await wrapper()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.es_host,
                                verify_certs=False)
    try:
        await backoff_handler(client.ping)
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture(name='es_write_data')
async def es_write_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        if await es_client.indices.exists(index=kwargs['_index']):
            await es_client.indices.delete(index=kwargs['_index'])
        await es_client.indices.create(index=kwargs['_index'],
                                       **kwargs['_mapping'])

        updated, errors = await backoff_handler(
            async_bulk,
            client=es_client,
            actions=kwargs['_data'],
            refresh='wait_for')

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    yield inner


@pytest_asyncio.fixture(name='es_search_data')
async def es_search_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        try:
            doc = await backoff_handler(
                es_client.search,
                index=kwargs['index'],
                body=kwargs['body'])
            return [hit["_source"] for hit in doc["hits"]["hits"]]
        except NotFoundError:
            return []

    yield inner


@pytest_asyncio.fixture(name='es_get_data')
async def es_get_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        try:
            return await backoff_handler(
                es_client.get,
                index=kwargs['index'],
                id=kwargs['id'])
        except NotFoundError:
            return []

    yield inner


@pytest_asyncio.fixture(scope='session', name='redis_client')
async def redis_client():
    redis_client = aioredis.Redis(host=test_settings.redis_host,
                                  port=test_settings.redis_port,
                                  decode_responses=True)
    await backoff_handler(redis_client.ping)
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(name='redis_get_key')
async def redis_get_key(redis_client: aioredis.Redis):
    async def inner(key_name):
        return await backoff_handler(redis_client.get, key_name)
    yield inner


@pytest_asyncio.fixture(scope='session', name='api_client')
async def api_client():
    api = aiohttp.ClientSession()
    yield api
    await api.close()


@pytest_asyncio.fixture(name='api_get_query')
async def api_get_query(api_client: aiohttp.ClientSession):
    async def inner(**kwargs):
        async with await backoff_handler(
              api_client.get, kwargs['url'],
              params=kwargs.get('query_data'),
              ssl=False) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status
    yield inner


@pytest_asyncio.fixture(name='get_data_test')
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
