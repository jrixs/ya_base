from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres import get_session
from schemas.user import UserCreate, UserResponse
from services.registration import RegService

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.auth_data import User

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    existing_user_query = db.execute(select(User).filter(User.email == user.email))
    existing_user = existing_user_query.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    
    db_user = await RegService.create_user(db, user)
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role_id=db_user.role_id,
        joined_at=db_user.joined_at.isoformat(),
        updated_at=db_user.updated_at.isoformat()
    )