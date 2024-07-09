from http import HTTPStatus
from typing import Optional

from models.person import Person, Persons
from services.person import (
    PersonService,
    PersonsService,
    get_person_service,
    get_persons_service,
)

from fastapi import APIRouter, Depends, HTTPException, Query

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Информация о персоне
@router.get(
    "/{person_id}",
    response_model=Person,
    description="Поиск конкретного человека",
)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:

    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person not found"
        )

    return person


# Все персоны
@router.get("/", response_model=Persons, description="Поиск по людям")
async def persons(
    persons_service: PersonsService = Depends(get_persons_service),
    name: Optional[str] = Query(
        None, title="Сортировка", description="Частичный поиск"
    ),
    page: int = Query(1, title="Страница", description="Номер страницы", ge=1),
    page_size: int = Query(
        10,
        title="Размер страницы",
        description="Количество элементов на странице",
        ge=1,
        le=100,
    ),
) -> Persons:

    persons = await persons_service.get_persons(
        name=name, page=page, page_size=page_size
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="persons not found"
        )

    return persons
