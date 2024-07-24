from fastapi import Request, status
from fastapi.responses import JSONResponse

import logging

logger = logging.getLogger()


def global_exception_handler(request: Request, exc: Exception):
    logger.info(f"Error occupied on request: {request.url}\n" f"Exception is {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc)
    )


class AccessTokenExpired(Exception):
    pass


class AccessTokenInvalid(Exception):
    pass


class RefreshTokenInvalid(Exception):
    pass


class IncorrectPasswordException(Exception):
    pass


class AccessTokenBlocked(Exception):
    pass


class RefreshTokenBlocked(Exception):
    pass


class AuthenticationIncorrect(Exception):
    pass

