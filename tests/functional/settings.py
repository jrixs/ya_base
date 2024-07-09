from pydantic import Field
from pydantic_settings import BaseSettings

from utils.get_mappings import read_json_file


class TestSettings(BaseSettings):

    es_host: str = 'http://127.0.0.1:9200'
    service_url: str = 'http://127.0.0.1'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    es_index_movies: str = Field(default='movies')
    es_id_field_movies: str = Field(default='id')
    es_index_mapping_movies: dict = Field(
        default=read_json_file("testdata/mappings_movies.json"))

    es_index_genres: str = Field(default='genres')
    es_id_field_genres: str = Field(default='id')
    es_index_mapping_genres: dict = Field(
        default=read_json_file("testdata/mappings_genres.json"))

    es_index_persons: str = Field(default='persons')
    es_id_field_persons: str = Field(default='id')
    es_index_mapping_persons: dict = Field(
        default=read_json_file("testdata/mappings_persons.json"))


test_settings = TestSettings()
