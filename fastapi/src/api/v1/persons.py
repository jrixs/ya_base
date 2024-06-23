from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from services.person import PersonService, get_person_service

from datetime import datetime, date

router = APIRouter()


# Модель для людей (актеров, сценаристов, режиссеров) ИЗМЕНИТСЯ
class Person(BaseModel):
    id: str
    full_name: str
    gender: str
    created: datetime
    modified: datetime


# Два варианта: поиск всех и по id
