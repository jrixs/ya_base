from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
from models.genre import Genre, Genres
from services.base_services import Cache, Storage
from services.base_services import BaseService, RedisCache, ElasticStorage

from fastapi import Depends


class GenreService(BaseService):

    def __init__(self, storage: Storage, cache: Cache):
        super().__init__(storage=storage, cache=cache)

    async def get(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_from_cache(genre_id)
        if not genre:
            genre = await self._get_from_storage(genre_id)
            if not genre:
                return None
            await self._set_to_cache(genre)
        return genre

    async def _get_from_storage(self, genre_id: str) -> Optional[Genre]:
        doc = await self._storage.get(_index="genres", _id=genre_id)
        try:
            return Genre(**doc["_source"])
        except NotFoundError:
            return None

    async def _get_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self._cache.get(f"genre:{genre_id}")
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _set_to_cache(self, genre: Genre):
        await self._cache.set(f"genre:{genre.id}", genre.json())


class GenresService(BaseService):

    def __init__(self, storage: Storage, cache: Cache):
        super().__init__(storage=storage, cache=cache)

    async def get(self, genre_name: str = '') -> Optional[Genres]:
        genres = await self._get_from_cache(genre_name)
        if not genres:
            genres = await self._get_from_storage(genre_name)
            if not genres:
                return None
            await self._set_to_cache(genre_name, genres)
        return genres

    async def _get_from_storage(self, genre_name: str) -> Optional[Genres]:
        if genre_name:
            order = "desc" if genre_name.startswith('-') else "asc"
        else:
            order = None

        body = {
            "_source": ["id", "genre"],
            "size": 100,
            "query": {
                "bool": {
                    "must": [{"match": {"genre": genre_name}}] if genre_name else [{"match_all": {}}]
                }
            },
            "sort": [
                {"genre": {"order": order}} if order else {}
            ]
        }
        data = {'genres': []}

        data = {"genres": []}
        doc = await self._storage.search(_index="genres", _body=body)
        if doc:
            data["genres"].extend(
                [hit["_source"] for hit in doc["hits"]["hits"]]
            )
        else:
            return None

        return Genres(**data)

    async def _get_from_cache(self, genre_name: str) -> Optional[Genres]:
        data = await self._cache.get(f'genres:{genre_name}')
        if not data:
            return None
        genre = Genres.parse_raw(data)
        return genre

    async def _set_to_cache(self, genre_name: str, genres: Genres):
        await self._cache.set(f'genres:{genre_name}', genres.json())


@lru_cache(maxsize=20)
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(storage=ElasticStorage(elastic),
                        cache=RedisCache(redis))


@lru_cache(maxsize=20)
def get_genres_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenresService:
    return GenresService(storage=ElasticStorage(elastic),
                         cache=RedisCache(redis))
