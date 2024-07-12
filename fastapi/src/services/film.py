from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
from services.base_services import Cache, Storage
from models.film import AllFilms, Film
from services.base_services import BaseService, RedisCache, ElasticStorage


from fastapi import Depends


class FilmService(BaseService):

    def __init__(self, storage: Storage, cache: Cache):
        super().__init__(storage=storage, cache=cache)

    async def get(self, film_id: str) -> Optional[Film]:
        film = await self._get_from_cache(film_id)
        if not film:
            film = await self._get_from_storage(film_id)
            if not film:
                return None
            await self._set_to_cache(film)
        return film

    async def _get_from_storage(self, film_id: str) -> Optional[Film]:
        doc = await self._storage.get(_index="movies", _id=film_id)
        try:
            return Film(**doc["_source"])
        except NotFoundError:
            return None

    async def _get_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        data = await self._cache.get(f"film:{film_id}")
        if not data:
            return None
        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _set_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        await self._cache.set(f"film:{film.id}", film.json())


class FilmsService(BaseService):

    def __init__(self, storage: Storage, cache: Cache):
        super().__init__(storage=storage, cache=cache)

    async def get(
        self,
        filtr: str = "",
        search: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> Optional[AllFilms]:
        films = await self._get_from_cache(filtr, search, page, page_size)
        if not films:
            films = await self._get_from_storage(
                filtr, search, page, page_size
            )
            if not films:
                return None
            await self._set_to_cache(
                filtr, search, page, page_size, films
            )
        return films

    async def _get_from_storage(
        self, filtr: str, search: str, page: int, page_size: int
    ) -> Optional[AllFilms]:
        body = {
            "_source": ["id", "imdb_rating", "genres", "title"],
            "query": {"bool": {"must": [], "filter": []}},
            "size": page_size,
            "from": (page - 1) * page_size,
        }

        if search:
            search_query = {"multi_match": {"query": search, "fields": ["*"]}}
            body["query"]["bool"]["must"].append(search_query)

        if filtr:
            order = "desc" if filtr.startswith("-") else "asc"
            sort_by = filtr.lstrip("-")
            body["sort"] = [{sort_by: {"order": order}}]

        data = {"movies": []}
        doc = await self._storage.search(_index="movies", _body=body)
        if doc:
            data["movies"].extend(
                [hit["_source"] for hit in doc["hits"]["hits"]]
            )
        else:
            return None

        return AllFilms(**data)

    async def _get_from_cache(
        self, filtr: str, search: str, page: int, page_size: int
    ) -> Optional[AllFilms]:
        cache_key = f"{filtr}_{search}_{page}_{page_size}_films"
        data = await self._cache.get(cache_key)
        if not data:
            return None
        films = AllFilms.parse_raw(data)
        return films

    async def _set_to_cache(
        self,
        filtr: str,
        search: str,
        page: int,
        page_size: int,
        films: AllFilms,
    ):
        cache_key = f"{filtr}_{search}_{page}_{page_size}_films"
        await self._cache.set(cache_key, films.json())


@lru_cache(maxsize=20)
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(storage=ElasticStorage(elastic),
                       cache=RedisCache(redis))


@lru_cache(maxsize=20)
def get_films_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsService:
    return FilmsService(storage=ElasticStorage(elastic),
                        cache=RedisCache(redis))
