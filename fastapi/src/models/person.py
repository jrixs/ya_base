from typing import List

from pydantic import BaseModel


class PersonsItems(BaseModel):
    id: str
    full_name: str


class PersonItems(BaseModel):
    id: str
    title: str
    imdb_rating: float


# Список всех жанров
class Persons(BaseModel):
    persons: List[PersonsItems]


# Информация по одному жанру
class Person(BaseModel):
    id: str
    full_name: str
    films: List[PersonItems]
