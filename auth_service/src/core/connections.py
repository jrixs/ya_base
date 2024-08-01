from typing import Optional
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from loguru import logger

from core.config import settings

engine = create_async_engine(settings.database_async_url, echo=False)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
redis_connect: Optional[Redis] = None


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> Redis:
    try:
        return redis_connect
    except Exception as e:
        logger.info(f"Redis stopped: {e}")
