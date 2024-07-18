from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Название проекта
    project_name: str = Field("Сервис аторизации", env="PROJECT_NAME")

    # Настройка БД
    db_host: str = Field("127.0.0.1", env="DB_HOST")
    db_port: str = Field("5432", env="DB_PORT")
    db_name: str = Field("movies_auth", env="DB_NAME")
    db_user: str = Field("auth", env="DB_USER")
    db_password: str = Field("123qwe", env="DB_PASSWORD")

    # Настройки Redis
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")

    # Корень проекта
    base_dir: str = Field("/src", env="BASE_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
