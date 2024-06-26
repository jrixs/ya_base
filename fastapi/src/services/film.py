from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, AllFilms

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
        data = await self.redis.get(film_id)
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
            film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )


class FilmsService(Base):

    async def get_films(
        self, filtr: str = "", search: str = ""
    ) -> Optional[AllFilms]:
        films = await self._films_from_cache(filtr, search)
        if not films:
            films = await self._get_films_from_elastic(filtr, search)
            if not films:
                return None
            await self._put_films_to_cache(filtr, search, films)
        print(films)
        return films

    async def _get_films_from_elastic(
        self, filtr: str, search: str
    ) -> Optional[AllFilms]:
        body = {
            "_source": [
                "id",
                "imdb_rating",
                "genres",
                "title",
            ],  # Указание полей, которые нужно вернуть
            "query": {"bool": {"must": [], "filter": []}},
            "size": 100,  # Устанавливаем размер результата на 100 документов
        }

        # Условие для поиска
        if search:
            search_query = {"multi_match": {"query": search, "fields": ["*"]}}
            body["query"]["bool"]["must"].append(search_query)

        # Условие для сортировки
        if filtr:
            order = "desc" if filtr.startswith("-") else "asc"
            sort_by = filtr.lstrip("-")

            # Условие для сортировки
            body["sort"] = [{sort_by: {"order": order}}]

        data = {"movies": []}
        try:
            doc = await self.elastic.search(
                index="movies", body=body, scroll="1m"
            )
            while len(doc["hits"]["hits"]):
                data["movies"].extend(
                    [hit["_source"] for hit in doc["hits"]["hits"]]
                )
                scroll_id = doc["_scroll_id"]
                doc = await self.elastic.scroll(
                    scroll_id=scroll_id, scroll="1m"
                )

        except NotFoundError:
            return None

        return AllFilms(**data)

    async def _films_from_cache(
        self, filtr: str, search: str
    ) -> Optional[AllFilms]:
        cache_key = f"{filtr}_{search}_films"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        films = AllFilms.parse_raw(data)
        return films

    async def _put_films_to_cache(
        self, filtr: str, search: str, films: AllFilms
    ):
        cache_key = f"{filtr}_{search}_films"
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
