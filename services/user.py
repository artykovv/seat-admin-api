# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi_users.password import PasswordHelper
from models import User
from schemas.user import UserCreate, UserUpdate
from uuid import UUID

class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: UUID):
        result = await db.execute(
            select(User)
            .filter(User.id == user_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate):
        db_user = await UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password" and value:
                value = UserService.password_helper.hash(value)
            else:
                setattr(db_user, key, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID):
        db_user = await UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        await db.delete(db_user)
        await db.commit()
        return db_user