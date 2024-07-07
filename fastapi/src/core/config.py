from pydantic import Field
from pydantic_settings import BaseSettings
from core.logger import LOGGING


class Settings(BaseSettings):
    # Применяем настройки логирования
    logging_config: dict = Field(LOGGING, env='LOGGING')

    # Название проекта. Используется в Swagger-документации
    project_name: str = Field('backend_movies', env='PROJECT_NAME')

    # Настройки Redis
    redis_host: str = Field('redis', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    # Настройки Elasticsearch
    elastic_schema: str = Field('http://', env='ELASTIC_SCHEMA')
    elastic_host: str = Field('elasticsearch', env='ELASTIC_HOST')
    elastic_port: int = Field(9200, env='ELASTIC_PORT')

    # Корень проекта
    base_dir: str = Field("/src", env='BASE_DIR')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
