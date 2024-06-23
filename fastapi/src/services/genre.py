from functools import lru_cache
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre, Genres

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Base:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


class GenreService(Base):

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            genre.id, genre.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )


class GenresService(Base):

    async def get_genres(self) -> Optional[Genres]:
        ganres = await self._genres_from_cache()
        if not ganres:
            ganres = await self._get_genres_from_elastic()
            if not ganres:
                return None
            await self._put_genres_to_cache(ganres)
        return ganres

    async def _get_genres_from_elastic(self) -> Optional[Genres]:
        body = {
            "_source": ["id", "genre"],
            "size": 100,
            "query": {
                "match_all": {}
            }
        }

        try:
            doc = await self.elastic.search(index='genres', body=body,
                                            scroll='1m')
        except NotFoundError:
            return None
        data = {'genres': [_['_source'] for _ in doc['hits']['hits']]}
        return Genres(**data)

    async def _genres_from_cache(self) -> Optional[Genres]:
        data = await self.redis.get('ganres')
        if not data:
            return None
        ganre = Genres.parse_raw(data)
        return ganre

    async def _put_genres_to_cache(self, ganres: Genres):
        await self.redis.set(
            'ganres', ganres.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )


@lru_cache(maxsize=20)
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)


@lru_cache(maxsize=20)
def get_genres_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenresService:
    return GenresService(redis, elastic)
