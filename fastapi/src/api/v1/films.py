from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from services.film import (
    FilmService,
    FilmsService,
    get_film_service,
    get_films_service,
    Film,
    AllFilms,
)

router = APIRouter()


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

    return film


# Все фильмы
@router.get("/", response_model=AllFilms)
async def films(
    films_service: FilmsService = Depends(get_films_service),
    order_by: Optional[str] = Query(
        None, title="Order_by", description="sort"
    ),
    search: Optional[str] = Query(
        None, title="Search", description="Full text search"
    ),
) -> AllFilms:

    films = await films_service.get_films(filtr=order_by, search=search)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="films not found"
        )

    return films
