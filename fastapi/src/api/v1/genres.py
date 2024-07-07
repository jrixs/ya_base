from http import HTTPStatus
from typing import Optional

from models.genre import Genre, Genres
from services.genre import (GenreService, GenresService, get_genre_service,
                            get_genres_service)

from fastapi import APIRouter, Depends, HTTPException, Query

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Информация о жанре
@router.get("/{genre_id}", response_model=Genre)
async def genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')

    return genre


# Все жанры
@router.get('/', response_model=Genres)
async def genres(
    genres_service: GenresService = Depends(get_genres_service),
    filtr: Optional[str] = Query(None, title="Name Filter", description="Filter persons by name")
) -> Genres:

    genres = await genres_service.get_genres(filtr=filtr)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genres not found')

    return genres
