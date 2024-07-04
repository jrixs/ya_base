from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # es_host: str = Field('http://elasticsearch:9200', env='ELASTIC_HOST')
    # service_url: str = Field('http://nginx', env='SERVICE_URL')

    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    service_url: str = Field('http://127.0.0.1', env='SERVICE_URL')

    es_index_movies: str = Field('movies', env='ELASTIC_INDEX_MOVIES')
    es_id_field_movies: str = Field('id', env='ELASTIC_ID_FIELD_MOVIES')
    es_index_mapping_movies: dict = Field({}, env='ELASTIC_MAPPING_MOVIES')

    es_index_movies: str = Field('movies', env='ELASTIC_INDEX_MOVIES')
    es_id_field_movies: str = Field('id', env='ELASTIC_ID_FIELD_MOVIES')
    es_index_mapping_movies: dict = Field({}, env='ELASTIC_MAPPING_MOVIES')

    es_index_movies: str = Field('movies', env='ELASTIC_INDEX_MOVIES')
    es_id_field_movies: str = Field('id', env='ELASTIC_ID_FIELD_MOVIES')
    es_index_mapping_movies: dict = Field({}, env='ELASTIC_MAPPING_MOVIES')

    redis_host: str = Field('redis', env='REDIS_HOST')


test_settings = TestSettings()
