from elasticsearch import AsyncElasticsearch
from settings import test_settings
import redis.asyncio as aioredis


async def es_client() -> AsyncElasticsearch:
    client = AsyncElasticsearch(hosts=test_settings.es_host,
                                verify_certs=False)
    return client


async def redis_client():
    client = aioredis.Redis(host=test_settings.redis_host,
                            port=test_settings.redis_port,
                            decode_responses=True)
    return client


async def redis_get_key(key_name):
    client = await redis_client()
    value = await client.get(key_name)
    await client.aclose()
    return value
