
from elasticsearch import AsyncElasticsearch, NotFoundError
from settings import test_settings
import redis.asyncio as aioredis
import pytest_asyncio
import aiohttp
from elasticsearch.helpers import async_bulk


@pytest_asyncio.fixture(name='es_client')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host,
                                   verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_write_data')
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


@pytest_asyncio.fixture(name='es_search_data')
async def es_search_data(es_client: AsyncElasticsearch):
    async def inner(**kwargs):
        {'search': 'The Star', 'page': '1', 'page_size': '25'},
        body = {
            "_source": ["id", "imdb_rating", "genres", "title"],
            "query": {"bool": {"must": [], "filter": []}},
            "size": int(kwargs['page_size']),
            "from": (int(kwargs['page']) - 1) * int(kwargs['page_size']),
        }

        if kwargs.get('search'):
            search_query = {"multi_match": {
                "query": kwargs.get('search'), "fields": ["*"]}}
            body["query"]["bool"]["must"].append(search_query)

        if kwargs.get('order_by'):
            order = "desc" if kwargs.get('order_by').startswith("-") else "asc"
            sort_by = kwargs.get('order_by').lstrip("-")
            body["sort"] = [{sort_by: {"order": order}}]

        try:
            doc = await es_client.search(index=kwargs['index'], body=body)
            return [hit["_source"] for hit in doc["hits"]["hits"]]
        except NotFoundError:
            return []

    yield inner


@pytest_asyncio.fixture(name='redis_client')
async def redis_client():
    redis_client = aioredis.Redis(host=test_settings.redis_host,
                                  port=test_settings.redis_port,
                                  decode_responses=True)
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(name='redis_get_key')
async def redis_get_key(redis_client: aioredis.Redis):
    async def inner(key_name):
        return await redis_client.get(key_name)
    yield inner


@pytest_asyncio.fixture(name='api_client')
async def api_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='api_get_query')
async def api_get_query(api_client: aiohttp.ClientSession):
    async def inner(**kwargs):
        async with api_client.get(kwargs['url'], params=kwargs['query_data'],
                                  ssl=False) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status
    yield inner
