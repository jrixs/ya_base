from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from models.genre import Genre, Genres
from services.genre import GenreService, get_genre_service
from services.genre import GenresService, get_genres_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Информация о жанре
@router.get('/{ganre_id}', response_model=Genre)
async def ganre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre:

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='ganre not found')

    return genre


# Все жанры
@router.get('/', response_model=Genres)
async def ganres(
    genres_service: GenresService = Depends(get_genres_service)
) -> Genres:

    genres = await genres_service.get_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='ganres not found')

    return genres
