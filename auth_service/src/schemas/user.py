from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role_id: UUID
    joined_at: str
    updated_at: str

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class UserData(BaseModel):
    id: str
    username: str
    email: EmailStr
    role_id: str
    is_superuser: bool
    access_token: str | None = None
    refresh_token: str | None = None


class RegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegistrationResponse(BaseModel):
    id: UUID
    access_token: str
    refresh_token: str


class BasePagination(BaseModel):
    limit: int = 0
    offset: int = 0


class UserHistory(BaseModel):
    id: UUID
    last_logged_at: datetime
    user_agent: str


class UserHistoryResponse(BaseModel):
    total_count: int
    data: list[UserHistory]
