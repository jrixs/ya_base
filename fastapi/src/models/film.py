# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from typing import List, Optional
from pydantic import BaseModel


# Модель для фильмов
class Film(BaseModel):
    id: str
    imdb_rating: Optional[float]
    genres: Optional[List[str]]
    title: Optional[str]
    description: Optional[str]
    directors_names: Optional[List[str]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    directors: Optional[List[dict]]
    actors: Optional[List[dict]]
    writers: Optional[List[dict]]


# Модель для всех фильмов
class AllFilmsBase(BaseModel):
    id: str
    imdb_rating: Optional[float]
    genres: Optional[List[str]]
    title: Optional[str]


class AllFilms(BaseModel):
    movies: List[AllFilmsBase]
