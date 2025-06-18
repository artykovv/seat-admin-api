from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from auth.fastapi_users_instance import fastapi_users
from config.database import get_async_session
from schemas.sections import SectionCreate, SectionUpdate, SectionResponse
from services.section import SectionCRUD
from typing import List

router = APIRouter(prefix="/sections", tags=["sections"])

@router.post("/", response_model=SectionResponse)
async def create_section(data: SectionCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await SectionCRUD.create(data, session)

@router.get("/{section_id}", response_model=SectionResponse)
async def get_section(section_id: int, session: AsyncSession = Depends(get_async_session)):
    return await SectionCRUD.get(session, section_id)

@router.get("/", response_model=List[SectionResponse])
async def get_sections(session: AsyncSession = Depends(get_async_session)):
    return await SectionCRUD.get(session)

@router.put("/{section_id}", response_model=SectionResponse)
async def update_section(section_id: int, data: SectionUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await SectionCRUD.update(section_id, data, session)

@router.delete("/{section_id}")
async def delete_section(section_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await SectionCRUD.delete(section_id, session)