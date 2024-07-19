from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.base import Base

engine = create_engine(settings.database_url, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# Функция понадобится при внедрении зависимостей
# Dependency
def get_session() -> SessionLocal:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def purge_database():
    session = next(get_session())
    session.execute("drop schema auth_service;")
    session.execute("drop schema auth_data;")
    session.execute("drop schema auth_secret;")
    session.execute("drop table alembic_version;")
    session.commit()
