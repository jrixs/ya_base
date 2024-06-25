from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.film import FilmService, get_film_service, Film, AllFilms

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


# Добавляем эндпоинт для получения списка фильмов
@router.get("/", response_model=List[AllFilms])
async def get_films(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    person: Optional[str] = Query(None, description="Filter by person"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    limit: int = Query(
        100, description="Number of results to return"
    ),  # тут количество указать можно
    offset: int = Query(0, description="Number of results to skip"),
    film_service: FilmService = Depends(get_film_service),
) -> List[AllFilms]:
    query = {
        "from": offset,
        "size": limit,
        "query": {"bool": {"must": [], "filter": []}},
    }

    if genre:
        query["query"]["bool"]["filter"].append({"term": {"genres": genre}})

    if person:
        person_query = {
            "multi_match": {
                "query": person,
                "fields": ["writers_names", "directors_names", "actors_names"],
            }
        }
        query["query"]["bool"]["must"].append(person_query)

    if sort_by:
        query["sort"] = [{sort_by: {"order": "asc"}}]

    try:
        result = await film_service.elastic.search(index="movies", body=query)
        films = [AllFilms(**hit["_source"]) for hit in result["hits"]["hits"]]
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return films
