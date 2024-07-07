from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from models.genre import Genre, Genres
from redis.asyncio import Redis

from fastapi import Depends

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
        data = await self.redis.get(f"genre:{genre_id}")
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            f"genre:{genre.id}", genre.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )


class GenresService(Base):

    async def get_genres(self, filtr: str = '') -> Optional[Genres]:
        genres = await self._genres_from_cache(filtr)
        if not genres:
            genres = await self._get_genres_from_elastic(filtr)
            if not genres:
                return None
            await self._put_genres_to_cache(filtr, genres)
        return genres

    async def _get_genres_from_elastic(self, filtr: str) -> Optional[Genres]:
        if filtr:
            order = "desc" if filtr.startswith('-') else "asc"
        else:
            order = None

        body = {
            "_source": ["id", "genre"],
            "size": 100,
            "query": {
                "bool": {
                    "must": [{"match": {"genre": filtr}}] if filtr else [{"match_all": {}}]
                }
            },
            "sort": [
                {"genre.keyword": {"order": order}} if order else {}
            ]
        }
        print(body)
        data = {'genres': []}

        try:
            doc = await self.elastic.search(index='genres', body=body,
                                            scroll='1m')
            while len(doc['hits']['hits']):
                data['genres'].extend([hit['_source'] for hit in doc['hits']['hits']])
                scroll_id = doc['_scroll_id']
                doc = await self.elastic.scroll(scroll_id=scroll_id, scroll='1m')

        except NotFoundError:
            return None
        return Genres(**data)

    async def _genres_from_cache(self, filtr: str) -> Optional[Genres]:
        data = await self.redis.get(f'{filtr}_genres')
        if not data:
            return None
        genre = Genres.parse_raw(data)
        return genre

    async def _put_genres_to_cache(self, filtr: str, genres: Genres):
        await self.redis.set(
            f'{filtr}_genres', genres.json(), FILM_CACHE_EXPIRE_IN_SECONDS
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
