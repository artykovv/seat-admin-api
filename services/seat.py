from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from schemas.seats import SeatCreate, SeatResponse, SeatUpdate
from models import Seat

class SeatCRUD:
    @staticmethod
    async def create(data: SeatCreate, session: AsyncSession):
        seat = Seat(**data.dict())
        session.add(seat)
        await session.commit()
        await session.refresh(seat)
        return SeatResponse.from_orm(seat)

    @staticmethod
    async def get(session: AsyncSession, seat_id: int = None) -> List[SeatResponse] | SeatResponse:
        if seat_id:
            stmt = select(Seat).where(Seat.id == seat_id)
            result = await session.execute(stmt)
            seat = result.scalars().first()
            if not seat:
                raise HTTPException(status_code=404, detail="Seat not found")
            return SeatResponse.from_orm(seat)
        stmt = select(Seat)
        result = await session.execute(stmt)
        return [SeatResponse.from_orm(s) for s in result.scalars().all()]

    @staticmethod
    async def update(seat_id: int, data: SeatUpdate, session: AsyncSession):
        stmt = select(Seat).where(Seat.id == seat_id)
        result = await session.execute(stmt)
        seat = result.scalars().first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(seat, key, value)
        await session.commit()
        await session.refresh(seat)
        return SeatResponse.from_orm(seat)

    @staticmethod
    async def delete(seat_id: int, session: AsyncSession):
        stmt = select(Seat).where(Seat.id == seat_id)
        result = await session.execute(stmt)
        seat = result.scalars().first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found")
        await session.delete(seat)
        await session.commit()
        return {"message": "Seat deleted successfully"}