from pydantic import BaseModel


class JWTtokens(BaseModel):
    id: str
    role: str
    is_superuser: bool
    access_token: str
    refresh_token: str
