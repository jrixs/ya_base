from functools import lru_cache
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person, Persons
from services.base_services import Cache, Storage
from services.base_services import BaseService, RedisCache, ElasticStorage


class PersonService(BaseService):

    def __init__(self, storage: Storage, cache: Cache):
        super().__init__(storage=storage, cache=cache)

    async def get(self, person_id: str) -> Optional[Person]:
        person = await self._get_from_cache(person_id)
        if not person:
            person = await self._get_from_storage(person_id)
            if not person:
                return None
            await self._set_to_cache(person)
        return person

    async def _get_from_storage(self, person_id: str) -> Optional[Person]:
        doc = await self._storage.get(_index="persons", _id=person_id)
        try:
            return Person(**doc["_source"])
        except NotFoundError:
            return None

    async def _get_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self._cache.get(f"person:{person_id}")
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _set_to_cache(self, person: Person):
        await self._cache.set(f"person:{person.id}", person.json())


class PersonsService(BaseService):

    def __init__(self, storage: Storage, cache: Cache):
        super().__init__(storage=storage, cache=cache)

    async def get(self, page: int, page_size: int,
                  name: str = '') -> Optional[Persons]:
        persons = await self._get_from_cache(name, page, page_size)
        if not persons:
            persons = await self._get_from_storage(
                name, page, page_size)
            if not persons:
                return None
            await self._set_to_cache(name, persons, page, page_size)
        return persons

    async def _get_from_storage(self, name: str, page: int,
                                page_size: int) -> Optional[Persons]:

        if name:
            order = "desc" if name.startswith('-') else "asc"
        else:
            order = None

        body = {
            "_source": ["id", "full_name"],
            "query": {"bool": {
                "must": [{"match": {
                    "full_name": name}}] if name else [{"match_all": {}}]
                }
            },
            "sort": [{"full_name": {"order": order}} if order else {}],
            "size": page_size,
            "from": (page - 1) * page_size,
        }

        doc = await self._storage.search(_index="persons", _body=body)
        if doc:
            data = {'persons': [hit['_source'] for hit in doc['hits']['hits']]}
        else:
            return None

        return Persons(**data)

    async def _get_from_cache(self, name: str, page: int,
                              page_size: int) -> Optional[Persons]:
        data = await self._cache.get(f'persons:{name}_{page}_{page_size}')
        if not data:
            return None
        persons = Persons.parse_raw(data)
        return persons

    async def _set_to_cache(self, name: str, persons: Persons,
                            page: int, page_size: int):
        await self._cache.set(f'persons:{name}_{page}_{page_size}',
                              persons.json())


@lru_cache(maxsize=20)
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(storage=ElasticStorage(elastic),
                         cache=RedisCache(redis))


@lru_cache(maxsize=20)
def get_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonsService:
    return PersonsService(storage=ElasticStorage(elastic),
                          cache=RedisCache(redis))
