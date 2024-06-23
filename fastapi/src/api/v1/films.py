from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from services.film import FilmService, get_film_service

from datetime import datetime, date

router = APIRouter()


class Film(BaseModel):
    id: str
    imdb_rating: Optional[float] = None
    genres: Optional[List[str]] = None
    title: Optional[str] = None
    directors_names: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    directors: Optional[List[dict]] = None
    actors: Optional[List[dict]] = None
    writers: Optional[List[dict]] = None


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Film not found"
        )

    return Film(
        id=film.id,
        imdb_rating=film.imdb_rating,
        genres=film.genres,
        title=film.title,
        directors_names=film.directors_names,
        actors_names=film.actors_names,
        writers_names=film.writers_names,
        directors=film.directors,
        actors=film.actors,
        writers=film.writers,
    )


# Добавляем эндпоинт для получения списка фильмов
@router.get("/", response_model=List[Film])
async def get_films(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    person: Optional[str] = Query(None, description="Filter by person"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    limit: int = Query(100, description="Number of results to return"), # тут количество указать можно
    offset: int = Query(0, description="Number of results to skip"),
    film_service: FilmService = Depends(get_film_service),
) -> List[Film]:
    query = {
        "from": offset,
        "size": limit,
        "query": {"bool": {"must": [], "filter": []}},
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
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return films
