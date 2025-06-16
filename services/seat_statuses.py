from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from schemas.seat_statuses import SeatStatusCreate, SeatStatusResponse, SeatStatusUpdate
from models import SeatStatus

class SeatStatusCRUD:
    @staticmethod
    async def create(data: SeatStatusCreate, session: AsyncSession):
        status = SeatStatus(**data.dict())
        session.add(status)
        await session.commit()
        await session.refresh(status)
        return SeatStatusResponse.from_orm(status)

    @staticmethod
    async def get(session: AsyncSession, status_id: int = None) -> List[SeatStatusResponse] | SeatStatusResponse:
        if status_id:
            stmt = select(SeatStatus).where(SeatStatus.id == status_id)
            result = await session.execute(stmt)
            status = result.scalars().first()
            if not status:
                raise HTTPException(status_code=404, detail="SeatStatus not found")
            return SeatStatusResponse.from_orm(status)
        stmt = select(SeatStatus)
        result = await session.execute(stmt)
        return [SeatStatusResponse.from_orm(s) for s in result.scalars().all()]

    @staticmethod
    async def update(status_id: int, data: SeatStatusUpdate, session: AsyncSession):
        stmt = select(SeatStatus).where(SeatStatus.id == status_id)
        result = await session.execute(stmt)
        status = result.scalars().first()
        if not status:
            raise HTTPException(status_code=404, detail="SeatStatus not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(status, key, value)
        await session.commit()
        await session.refresh(status)
        return SeatStatusResponse.from_orm(status)

    @staticmethod
    async def delete(status_id: int, session: AsyncSession):
        stmt = select(SeatStatus).where(SeatStatus.id == status_id)
        result = await session.execute(stmt)
        status = result.scalars().first()
        if not status:
            raise HTTPException(status_code=404, detail="SeatStatus not found")
        await session.delete(status)
        await session.commit()
        return {"message": "SeatStatus deleted successfully"}