from pydantic import BaseModel
from typing import List


class Persons_items(BaseModel):
    id: str
    full_name: str


class Person_items(BaseModel):
    id: str
    title: str
    imdb_rating: float


# Список всех жанров
class Persons(BaseModel):
    persons: List[Persons_items]


# Информация по одному жанру
class Person(BaseModel):
    id: str
    full_name: str
    films: List[Person_items]
