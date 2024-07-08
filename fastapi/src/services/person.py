from functools import lru_cache
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person, Persons
from services.base_services import Base, FILM_CACHE_EXPIRE_IN_SECONDS


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
        data = await self.redis.get(f"person:{person_id}")
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            f"person:{person.id}", person.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )


class PersonsService(Base):

    async def get_persons(self, page: int, page_size: int, 
                          name: str = '') -> Optional[Persons]:
        persons = await self._persons_from_cache(name, page, page_size)
        if not persons:
            persons = await self._get_persons_from_elastic(
                name, page, page_size)
            if not persons:
                return None
            await self._put_persons_to_cache(name, persons,
                                             page, page_size)
        return persons

    async def _get_persons_from_elastic(self, name: str, page: int,
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

        try:
            doc = await self.elastic.search(index='persons', body=body)
            data = {'persons': [hit['_source'] for hit in doc['hits']['hits']]}
        except NotFoundError:
            return None

        return Persons(**data)

    async def _persons_from_cache(self, name: str, page: int,
                                  page_size: int) -> Optional[Persons]:
        data = await self.redis.get(f'{name}_{page}_{page_size}_persons')
        if not data:
            return None
        persons = Persons.parse_raw(data)
        return persons

    async def _put_persons_to_cache(self, name: str, persons: Persons,
                                    page: int, page_size: int):
        await self.redis.set(
            f'{name}_{page}_{page_size}_persons',
            persons.json(), FILM_CACHE_EXPIRE_IN_SECONDS
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


