from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Union
from schemas.rows import RowCreate, RowResponse, RowUpdate
from models import Row

class RowCRUD:
    @staticmethod
    async def create(data: RowCreate, session: AsyncSession) -> RowResponse:
        row = Row(**data.dict())
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return RowResponse.from_orm(row)

    @staticmethod
    async def get(session: AsyncSession, row_id: int = None) -> Union[List[RowResponse], RowResponse]:
        if row_id:
            stmt = select(Row).where(Row.id == row_id)
            result = await session.execute(stmt)
            row = result.scalars().first()
            if not row:
                raise HTTPException(status_code=404, detail="Row not found")
            return RowResponse.from_orm(row)
        stmt = select(Row)
        result = await session.execute(stmt)
        return [RowResponse.from_orm(r) for r in result.scalars().all()]

    @staticmethod
    async def update(row_id: int, data: RowUpdate, session: AsyncSession) -> RowResponse:
        stmt = select(Row).where(Row.id == row_id)
        result = await session.execute(stmt)
        row = result.scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="Row not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(row, key, value)
        await session.commit()
        await session.refresh(row)
        return RowResponse.from_orm(row)

    @staticmethod
    async def delete(row_id: int, session: AsyncSession) -> dict:
        stmt = select(Row).where(Row.id == row_id)
        result = await session.execute(stmt)
        row = result.scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="Row not found")
        await session.delete(row)
        await session.commit()
        return {"message": "Row deleted successfully"}