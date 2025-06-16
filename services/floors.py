from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from schemas.floors import FloorCreate, FloorResponse, FloorUpdate
from models import Floor

class FloorCRUD:
    @staticmethod
    async def create(data: FloorCreate, session: AsyncSession):
        floor = Floor(**data.dict())
        session.add(floor)
        await session.commit()
        await session.refresh(floor)
        return FloorResponse.from_orm(floor)

    @staticmethod
    async def get(session: AsyncSession, floor_id: int = None) -> List[FloorResponse] | FloorResponse:
        if floor_id:
            stmt = select(Floor).where(Floor.id == floor_id)
            result = await session.execute(stmt)
            floor = result.scalars().first()
            if not floor:
                raise HTTPException(status_code=404, detail="Floor not found")
            return FloorResponse.from_orm(floor)
        stmt = select(Floor)
        result = await session.execute(stmt)
        return [FloorResponse.from_orm(f) for f in result.scalars().all()]

    @staticmethod
    async def update(floor_id: int, data: FloorUpdate, session: AsyncSession):
        stmt = select(Floor).where(Floor.id == floor_id)
        result = await session.execute(stmt)
        floor = result.scalars().first()
        if not floor:
            raise HTTPException(status_code=404, detail="Floor not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(floor, key, value)
        await session.commit()
        await session.refresh(floor)
        return FloorResponse.from_orm(floor)

    @staticmethod
    async def delete(floor_id: int, session: AsyncSession):
        stmt = select(Floor).where(Floor.id == floor_id)
        result = await session.execute(stmt)
        floor = result.scalars().first()
        if not floor:
            raise HTTPException(status_code=404, detail="Floor not found")
        await session.delete(floor)
        await session.commit()
        return {"message": "Floor deleted successfully"}