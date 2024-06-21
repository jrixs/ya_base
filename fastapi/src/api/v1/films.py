from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from services.film import FilmService, get_film_service

from datetime import datetime, date

router = APIRouter()


# Модель для фильмов
class Film(BaseModel):
    id: str
    title: str
    premiere_date: Optional[date]
    type: str
    rating: Optional[float]
    created: datetime
    modified: datetime

# Модель для жанров
class Genre(BaseModel):
    id: str
    name: str
    created: datetime
    modified: datetime

# Модель для людей (актеров, сценаристов, режиссеров)
class Person(BaseModel):
    id: str
    full_name: str
    gender: str
    created: datetime
    modified: datetime

# Модель для связи между фильмами и жанрами
class GenreFilmWork(BaseModel):
    id: str
    film_work_id: str
    genre_id: str
    created: datetime

# Модель для связи между фильмами и людьми (актеры, сценаристы, режиссеры)
class PersonFilmWork(BaseModel):
    id: str
    film_work_id: str
    person_id: str
    role: str
    created: datetime


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')

    return Film(
        id=film.id,
        title=film.title,
        premiere_date=film.premiere_date,
        type=film.type,
        rating=film.rating,
        created=film.created,
        modified=film.modified
    )

# Добавляем эндпоинт для получения списка фильмов
@router.get('/', response_model=List[Film])
async def get_films(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    person: Optional[str] = Query(None, description="Filter by person"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    limit: int = Query(10, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    query = {
        "from": offset,
        "size": limit,
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        }
    }

    if genre:
        query["query"]["bool"]["filter"].append({"term": {"genre": genre}})
    
    if person:
        query["query"]["bool"]["filter"].append({"term": {"person": person}})
    
    if sort_by:
        query["sort"] = [{sort_by: {"order": "asc"}}]

    try:
        result = await film_service.elastic.search(index="movies", body=query)
        films = [Film(**hit["_source"]) for hit in result["hits"]["hits"]]
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    return films

