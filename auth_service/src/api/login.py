from fastapi import APIRouter, status, Body, HTTPException, Depends
from responses.login import JWTtokens
from schemas.login import TokensService
from services.login import get_tokens

router = APIRouter()


@router.post("/",
             summary="Авторизация пользователя",
             description="Авторизация пользователя и выдача JWT токена.",
             status_code=status.HTTP_201_CREATED
             )
async def login(
    service_login: TokensService = Depends(get_tokens),
    login: str = Body(..., embed=True),
    password: str = Body(..., embed=True)
) -> JWTtokens:
    tokens = await service_login.get(login=login, password=password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You entered the wrong username or password."
        )
    return JWTtokens(**tokens.dict())
