from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TokensService(BaseModel):
    id: str
    username: str
    email: str
    role_id: str
    is_superuser: bool
    joined_at: datetime
    updated_at: datetime
    secret: str
    role: str
    access_token: Optional[str]
    refresh_token: Optional[str]


class LoginRequest(BaseModel):
    username: str
    password: str
