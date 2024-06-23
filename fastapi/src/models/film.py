# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from typing import List, Optional
from pydantic import BaseModel


# Модель для фильмов
class Film(BaseModel):
    id: str
    imdb_rating: Optional[float] = None
    genres: Optional[List[str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    directors_names: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    directors: Optional[List[dict]] = None
    actors: Optional[List[dict]] = None
    writers: Optional[List[dict]] = None
