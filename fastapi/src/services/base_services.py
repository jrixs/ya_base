from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
from abc import ABC, abstractmethod
from typing import Any, Dict, List


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Base:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


class Storage(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs) -> Any | None:
        pass

    @abstractmethod
    async def search(self, *args, **kwargs) -> Any | None:
        pass


class ElasticStorage(Storage):

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get(self, _index: str, _id: str) -> Dict | None:
        try:
            return await self.elastic.get(index=_index, id=_id)
        except NotFoundError:
            return None

    async def search(self, _index: str, _body: str) -> Dict | None:
        try:
            return await self.elastic.search(index=_index, body=_body)
        except NotFoundError:
            return None


class Cache(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs) -> Any | None:
        pass

    @abstractmethod
    async def set(self, *args, **kwargs) -> Any | None:
        pass


class RedisCache(Cache):

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, cache_key: str) -> str | None:
        return await self.redis.get(cache_key)

    async def set(self, cache_key: str, data: Dict | List) -> Any | None:
        await self.redis.set(cache_key, data, FILM_CACHE_EXPIRE_IN_SECONDS)


class BaseService(ABC):
    def __init__(self, storage: Storage, cache: Cache):
        self._storage = storage
        self._cache = cache

    @abstractmethod
    async def get(self, *args, **kwargs) -> Any | None:
        # TODO: общий запрос данных
        pass

    @abstractmethod
    async def _get_from_storage(self, *args, **kwargs) -> Any | None:
        # TODO: запрос данных у storage
        pass

    @abstractmethod
    async def _get_from_cache(self, *args, **kwargs) -> Any | None:
        # TODO: запрос данных в cache
        pass

    @abstractmethod
    async def _set_to_cache(self, *args, **kwargs) -> Any | None:
        # TODO: добавление данных в cache
        pass
