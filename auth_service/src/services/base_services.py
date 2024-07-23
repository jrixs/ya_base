
from redis.asyncio import Redis
from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Session
from loguru import logger


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 24 * 60 * 60  # 3 месяца


class DB(ABC):

    @abstractmethod
    async def insert(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def update(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def select(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def delete(self, *args, **kwargs) -> Any | None:
        ...


class PostgresDB(DB):

    def __init__(self, session: Session):
        self.session = session

    def insert(self, obj) -> Any | None:
        try:
            self.session.add(obj)
            self.session.commit()
            return obj.id
        except Exception as e:
            logger.error(e)
            self.session.rollback()
            return

    def update(self, statement) -> bool:
        try:
            self.session.execute(statement)
            self.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            self.session.rollback()
            return False

    def select(self, statement):
        try:
            self.session.execute(statement)
            return True
        except Exception as e:
            logger.error(e)
            return False

    def delete(self, statement):
        try:
            self.session.execute(statement)
            self.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            self.session.rollback()
            return False


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

    async def set(self, cache_key: str, data: dict | list) -> Any | None:
        await self.redis.set(cache_key, data, FILM_CACHE_EXPIRE_IN_SECONDS)


class BaseService(ABC):

    def __init__(self, db: PostgresDB, storage: RedisStorage):
        self._db = db
        self._storage = storage
