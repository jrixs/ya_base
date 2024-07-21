from sqlalchemy.ext.asyncio import AsyncSession
from models.auth_data import User
from models.auth_secret import Secret
from models.auth_service import Role
from core.passwd import hash_password
from schemas.user import UserCreate
import uuid
from sqlalchemy.future import select
from datetime import datetime

class RegService:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        role_id = "16191190-3781-4f94-8d66-92c2bcef7fea"
        existing_role_query = db.execute(select(Role).filter(Role.id == role_id))
        existing_role = existing_role_query.scalar_one_or_none()
        if not existing_role:
            role = Role(
            id = role_id,
            name = "test_role",
            user = []
            )
            db.add(role)

        hashed_password = hash_password(user.password)
        db_user = User(
            id=str(uuid.uuid4()),
            username=user.email.split('@')[0], 
            email=user.email, 
            role_id=role_id,  # Assuming a default role if not specified
            is_superuser=False,
            joined_at = str(datetime.now()),
            updated_at = str(datetime.now())
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        db_secret = Secret(
            id=str(uuid.uuid4()),
            user_id=db_user.id, 
            password=hashed_password, 
            updated_at = str(datetime.now())
        )
        db.add(db_secret)
        db.commit()
        db.refresh(db_secret)
        
        return db_user