from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})
    id: UUID
    username: str
    email: EmailStr
    role_id: UUID
    joined_at: datetime
    updated_at: datetime


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    email: EmailStr
    role_id: str | None
    is_superuser: bool
    access_token: str | None = None
    refresh_token: str | None = None


class BasePagination(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class UserHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    last_logged_at: datetime
    user_agent: str


class UserHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    history: list[UserHistory]
    total: int

