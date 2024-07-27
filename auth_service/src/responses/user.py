from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List, Any


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role_id: UUID
    joined_at: datetime
    updated_at: datetime


class UserHistoryResponse(BaseModel):
    id: UUID
    history: List[Any]
    total: int
