from functools import lru_cache
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person, Persons

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Base:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


class PersonService(Base):

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, Person: Person):
        await self.redis.set(
            Person.id, Person.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )


class PersonsService(Base):

    async def get_persons(self, name: str = '') -> Optional[Persons]:
        persons = await self._persons_from_cache(name)
        if not persons:
            persons = await self._get_persons_from_elastic(name)
            if not persons:
                return None
            await self._put_persons_to_cache(name, persons)
        return persons

    async def _get_persons_from_elastic(self, name: str) -> Optional[Persons]:

        if name:
            order = "desc" if name.startswith('-') else "asc"
        else:
            order = None

        body = {
            "_source": ["id", "full_name"],
            "size": 100,
            "query": {
                "bool": {
                    "must": [{"match": {"full_name": name}}] if name else [{"match_all": {}}]
                }
            },
            "sort": [
                {"full_name.keyword": {"order": order}} if order else {}
            ]
        }

        data = {'persons': []}
        try:
            doc = await self.elastic.search(index='persons', body=body,
                                            scroll='1m')
            while len(doc['hits']['hits']):
                data['persons'].extend([hit['_source'] for hit in doc['hits']['hits']])
                scroll_id = doc['_scroll_id']
                doc = await self.elastic.scroll(scroll_id=scroll_id, scroll='1m')
        except NotFoundError:
            return None

        return Persons(**data)

    async def _persons_from_cache(self, name: str) -> Optional[Persons]:
        data = await self.redis.get(f'{name}_persons')
        if not data:
            return None
        persons = Persons.parse_raw(data)
        return persons

    async def _put_persons_to_cache(self, name: str, persons: Persons):
        await self.redis.set(
            f'{name}_persons', persons.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )


@lru_cache(maxsize=20)
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)


@lru_cache(maxsize=20)
def get_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonsService:
    return PersonsService(redis, elastic)
