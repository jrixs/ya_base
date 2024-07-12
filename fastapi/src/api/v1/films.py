from http import HTTPStatus
from typing import Optional

from services.film import (
    AllFilms,
    Film,
    FilmService,
    FilmsService,
    get_film_service,
    get_films_service,
)

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    "/{film_id}", response_model=Film, description="Поиск конкретного фильма"
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Film not found"
        )

    return film


@router.get("/", response_model=AllFilms, description="Поиск по фильмам")
async def films(
    films_service: FilmsService = Depends(get_films_service),
    order_by: Optional[str] = Query(
        None, title="Сортировка", description="Сортировка фильмов"
    ),
    search: Optional[str] = Query(
        None, title="Поиск", description="Полнотекстовый поиск"
    ),
    page: int = Query(1, title="Страница", description="Номер страницы", ge=1),
    page_size: int = Query(
        10,
        title="Размер страницы",
        description="Количество элементов на странице",
        ge=1,
        le=100,
    ),
) -> AllFilms:
    films = await films_service.get(
        filtr=order_by, search=search, page=page, page_size=page_size
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Фильмы не найдены"
        )
    return films
