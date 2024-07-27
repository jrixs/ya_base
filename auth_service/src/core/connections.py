from typing import Optional
from redis.asyncio import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
redis_connect: Optional[Redis] = None


def get_session() -> SessionLocal:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_redis() -> Redis:
    try:
        return redis_connect
    except Exception as e:
        logger.info(f"Redis stopped: {e}")
