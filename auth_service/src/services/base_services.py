
from redis.asyncio import Redis
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 24 * 60 * 60  # 3 месяца


class DB(ABC):

    @abstractmethod
    async def insert(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def update(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def query(self, *args, **kwargs) -> Any | None:
        ...


class PostgresDB(DB):

    def __init__(self, session: AsyncSession):
        self.session = session

    def insert(self, obj) -> Any | None:
        try:
            self.session.add(obj)
            self.session.commit()
            return obj.id
        except Exception as e:
            print(e)
            self.session.rollback()
            return None

    def update(self, obj) -> bool:
        try:
            self.session.add(obj)
            self.session.commit()
            return True
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def query(self, obj, filter: dict):
        return self.session.query(obj).filter_by(**filter).first()


class Storage(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def set(self, *args, **kwargs) -> Any | None:
        ...


class RedisStorage(Storage):

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, cache_key: str) -> str | None:
        return await self.redis.get(cache_key)

    async def set(self, cache_key: str, data: Dict | List) -> Any | None:
        await self.redis.set(cache_key, data, FILM_CACHE_EXPIRE_IN_SECONDS)


class BaseService(ABC):

    def __init__(self, db: PostgresDB, storage: RedisStorage):
        self._db = db
        self._storage = storage
