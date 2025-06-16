from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from schemas.sections import SectionCreate, SectionResponse, SectionUpdate
from models import Section

class SectionCRUD:
    @staticmethod
    async def create(data: SectionCreate, session: AsyncSession):
        section = Section(**data.dict())
        session.add(section)
        await session.commit()
        await session.refresh(section)
        return SectionResponse.from_orm(section)

    @staticmethod
    async def get(session: AsyncSession, section_id: int = None) -> List[SectionResponse] | SectionResponse:
        if section_id:
            stmt = select(Section).where(Section.id == section_id)
            result = await session.execute(stmt)
            section = result.scalars().first()
            if not section:
                raise HTTPException(status_code=404, detail="Section not found")
            return SectionResponse.from_orm(section)
        stmt = select(Section)
        result = await session.execute(stmt)
        return [SectionResponse.from_orm(s) for s in result.scalars().all()]

    @staticmethod
    async def update(section_id: int, data: SectionUpdate, session: AsyncSession):
        stmt = select(Section).where(Section.id == section_id)
        result = await session.execute(stmt)
        section = result.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(section, key, value)
        await session.commit()
        await session.refresh(section)
        return SectionResponse.from_orm(section)

    @staticmethod
    async def delete(section_id: int, session: AsyncSession):
        stmt = select(Section).where(Section.id == section_id)
        result = await session.execute(stmt)
        section = result.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        await session.delete(section)
        await session.commit()
        return {"message": "Section deleted successfully"}