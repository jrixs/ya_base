from pydantic import Field
from pydantic_settings import BaseSettings

#??? тут наверное менять

class Settings(BaseSettings):

    # Название проекта. Используется в Swagger-документации
    project_name: str = Field("backend_movies", env="PROJECT_NAME")

    # Настройки Redis
    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")

    # Корень проекта
    base_dir: str = Field("/src", env="BASE_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()