
from redis.asyncio import Redis
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger


class DB(ABC):

    @abstractmethod
    async def insert(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def update(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def select_one(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def select_few(self, *args, **kwargs) -> Any | None:
        ...

    @abstractmethod
    async def delete(self, *args, **kwargs) -> Any | None:
        ...


class PostgresDB(DB):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, obj) -> Any | None:
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            return

    async def update(self, statement) -> Any:
        try:
            data = await self.session.execute(statement)
            await self.session.commit()
            return data
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            return False

    async def select_few(self, statement):
        try:
            data = await self.session.execute(statement)
            return data.all()
        except Exception as e:
            logger.error(e)
            return

    async def select_one(self, statement):
        try:
            data = await self.session.scalars(statement)
            return data.one_or_none()
        except Exception as e:
            logger.error(e)
            return

    async def delete(self, statement):
        try:
            await self.session.execute(statement)
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
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

    async def set(self,
                  cache_key: str,
                  data: Any,
                  expire: int
                  ) -> Any:
        await self.redis.set(cache_key, data, expire)


class BaseService(ABC):

    def __init__(self, db: PostgresDB, storage: RedisStorage):
        self._db = db
        self._storage = storage
