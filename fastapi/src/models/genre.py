from pydantic import BaseModel
from typing import List


class Genres_items(BaseModel):
    id: str
    genre: str


class Genre_items(BaseModel):
    id: str
    title: str
    imdb_rating: float


# Список всех жанров
class Genres(BaseModel):
    genres: List[Genres_items]


# Информация по одному жанру
class Genre(BaseModel):
    id: str
    genre: str
    films: List[Genre_items]
