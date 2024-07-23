from typing import Annotated

from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

from src.db.portgres import get_session

from auth_service.src.core.exception import AccessTokenExpired, AccessTokenInvalid, RefreshTokenInvalid
from auth_service.src.schemas.user import UserData

DBSession = Annotated[Session, Depends(get_session)]


def verify_user_access(
        request: Request,
) -> UserData:
    access_token: str = request.cookies.get("access_token")
    refresh_token: str = request.cookies.get("refresh_token")

    """здесь добавить поход в редис и проверку на протухший токен, если протух, то 401"""

    try:
        """декодятся данные и заполняется объект userdata, при возникновении ошибок - выбрасываем исключения"""
        data: UserData = decode_token(access_token)
    except AccessTokenExpired:
        """если рефреш токен нормальный, то он пересоздает access token, убирается в редис и создается новый рефреш. 
        иначе выбрасываем исключение"""
        data: UserData = verify_refresh_token(refresh_token)
        new_access_token, new_refresh_token = refresh_access_token(data)
        data.access_token = new_access_token
        data.refresh_token = new_refresh_token
    except (AccessTokenInvalid, RefreshTokenInvalid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    return data


VerifiedUser = Annotated[UserData, Depends(verify_user_access)]


def verify_user_admin_rights(user_data: VerifiedUser) -> UserData:
    if user_data.is_superuser:
        return user_data
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied"
        )


VerifiedAdmin = Annotated[UserData, Depends(verify_user_admin_rights)]
