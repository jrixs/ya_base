from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from models.film import AllFilms, Film
from redis.asyncio import Redis

from fastapi import Depends

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Base:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


class FilmService(Base):

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(f"film:{film_id}")
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            f"film:{film.id}", film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )


class FilmsService(Base):

    async def get_films(
        self,
        filtr: str = "",
        search: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> Optional[AllFilms]:
        films = await self._films_from_cache(filtr, search, page, page_size)
        if not films:
            films = await self._get_films_from_elastic(
                filtr, search, page, page_size
            )
            if not films:
                return None
            await self._put_films_to_cache(
                filtr, search, page, page_size, films
            )
        return films

    async def _get_films_from_elastic(
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
        try:
            doc = await self.elastic.search(index="movies", body=body)
            data["movies"].extend(
                [hit["_source"] for hit in doc["hits"]["hits"]]
            )
        except NotFoundError:
            return None

        return AllFilms(**data)

    async def _films_from_cache(
        self, filtr: str, search: str, page: int, page_size: int
    ) -> Optional[AllFilms]:
        cache_key = f"{filtr}_{search}_{page}_{page_size}_films"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        films = AllFilms.parse_raw(data)
        return films

    async def _put_films_to_cache(
        self,
        filtr: str,
        search: str,
        page: int,
        page_size: int,
        films: AllFilms,
    ):
        cache_key = f"{filtr}_{search}_{page}_{page_size}_films"
        await self.redis.set(
            cache_key, films.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache(maxsize=20)
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)


@lru_cache(maxsize=20)
def get_films_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsService:
    return FilmsService(redis, elastic)
