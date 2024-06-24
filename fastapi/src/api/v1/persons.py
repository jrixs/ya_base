from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query
from models.person import Person, Persons
from services.person import PersonService, get_person_service
from services.person import PersonsService, get_persons_service
from typing import Optional

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Информация о персоне
@router.get('/{person_id}', response_model=Person)
async def person_details(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> Person:

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='ganre not found')

    return person


# Все персоны
@router.get('/', response_model=Persons)
async def persons(
    persons_service: PersonsService = Depends(get_persons_service),
    name: Optional[str] = Query(None, title="Name Filter", description="Filter persons by name")
) -> Persons:

    persons = await persons_service.get_persons(name=name)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='ganres not found')

    return persons
