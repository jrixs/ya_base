from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from services.genre import GenreService, get_genre_service

from datetime import datetime, date

router = APIRouter()


# Модель для жанров ИЗМЕНИТСЯ
class Genre(BaseModel):
    id: str
    name: str
    created: datetime
    modified: datetime


# Два варианта: поиск всех и по id
