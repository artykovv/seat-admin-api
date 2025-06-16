from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from schemas.seat_categories import SeatCategoryCreate, SeatCategoryResponse, SeatCategoryUpdate
from models import SeatCategory

class SeatCategoryCRUD:
    @staticmethod
    async def create(data: SeatCategoryCreate, session: AsyncSession):
        category = SeatCategory(**data.dict())
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return SeatCategoryResponse.from_orm(category)

    @staticmethod
    async def get(session: AsyncSession, category_id: int = None) -> List[SeatCategoryResponse] | SeatCategoryResponse:
        if category_id:
            stmt = select(SeatCategory).where(SeatCategory.id == category_id)
            result = await session.execute(stmt)
            category = result.scalars().first()
            if not category:
                raise HTTPException(status_code=404, detail="SeatCategory not found")
            return SeatCategoryResponse.from_orm(category)
        stmt = select(SeatCategory)
        result = await session.execute(stmt)
        return [SeatCategoryResponse.from_orm(c) for c in result.scalars().all()]

    @staticmethod
    async def update(category_id: int, data: SeatCategoryUpdate, session: AsyncSession):
        stmt = select(SeatCategory).where(SeatCategory.id == category_id)
        result = await session.execute(stmt)
        category = result.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="SeatCategory not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(category, key, value)
        await session.commit()
        await session.refresh(category)
        return SeatCategoryResponse.from_orm(category)

    @staticmethod
    async def delete(category_id: int, session: AsyncSession):
        stmt = select(SeatCategory).where(SeatCategory.id == category_id)
        result = await session.execute(stmt)
        category = result.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="SeatCategory not found")
        await session.delete(category)
        await session.commit()
        return {"message": "SeatCategory deleted successfully"}