from http import HTTPStatus
from typing import Optional, Annotated

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


@router.get(
    '/',
    response_model=AllFilms,
    summary='Get all films',
    description='Get all films with filters, pagination and sorting',
)
async def films(
    order_by: Annotated[
        Optional[str], Query(title='Сортировка', description='Сортировка фильмов')
    ] = None,
    search: Annotated[
        Optional[str], Query(title='Поиск', description='Полнотекстовый поиск')
    ] = None,
    page: Annotated[
        int, Query(title='Страница', description='Номер страницы', ge=1)
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            title='Размер страницы',
            description='Количество элементов на странице',
            ge=1,
            le=100,
        ),
    ] = 10,
    films_service: FilmsService = Depends(get_films_service),
) -> AllFilms:
    if not (
        films := await films_service.get_films(
            filtr=order_by, search=search, page=page, page_size=page_size
        )
    ):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Фильмы не найдены'
        )
    return films


@router.get(
    '/{film_id}',
    response_model=Film,
    summary='Get film',
    description='Get film by uuid',
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    if not (film := await film_service.get_by_id(film_id)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')
    return film
