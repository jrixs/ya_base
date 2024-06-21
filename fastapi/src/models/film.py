# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from datetime import datetime, date
from typing import List
from pydantic import BaseModel

# Модель для фильмов
class Film(BaseModel):
    id: str
    title: str
    description: str
    premiere_date: date
    type: str
    rating: float
    file_path: str
    created: datetime
    modified: datetime

# Модель для жанров
class Genre(BaseModel):
    id: str
    name: str
    description: str
    created: datetime
    modified: datetime

# Модель для людей (актеров, сценаристов, режиссеров)
class Person(BaseModel):
    id: str
    full_name: str
    gender: str
    created: datetime
    modified: datetime
