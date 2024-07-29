import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from loguru import logger

from core.config import settings
from core.passwd import hash_password
from models.auth_data import User
from models.auth_secret import Secret


def create_default_superuser(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False)

    with SessionLocal() as db_session:
        statement = select(User).where(User.is_superuser)  # считаем, что суперюзер у нас единственный
        data = db_session.scalars(statement).one_or_none()

        if not data:
            user_id = str(uuid.uuid4())
            new_user = User(id=user_id,
                            username=settings.superuser_username,
                            email=settings.superuser_email,
                            is_superuser=True)
            new_password = Secret(
                id=str(uuid.uuid4()),
                user_id=user_id,
                password=hash_password(settings.superuser_password)
            )
            db_session.add(new_user)
            db_session.add(new_password)
            db_session.commit()


def main():
    logger.info("Starting superuser creation")
    engine = create_engine(settings.database_url, pool_pre_ping=True, echo=False)
    engine.connect()
    try:
        create_default_superuser(engine)
    except Exception as e:
        logger.warning("Superuser creation failed!")
        logger.error(e)
    engine.dispose()
    logger.info("Superuser creation ended")


main()
