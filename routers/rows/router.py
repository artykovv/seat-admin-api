from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from schemas.rows import RowCreate, RowUpdate, RowResponse
from services.rows import RowCRUD
from typing import List
from models import User
from auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/rows", tags=["rows"])

@router.post("/", response_model=RowResponse)
async def create_row(data: RowCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await RowCRUD.create(data, session)

@router.get("/{row_id}", response_model=RowResponse)
async def get_row(row_id: int, session: AsyncSession = Depends(get_async_session)):
    return await RowCRUD.get(session, row_id)

@router.get("/", response_model=List[RowResponse])
async def get_rows(session: AsyncSession = Depends(get_async_session)):
    return await RowCRUD.get(session)

@router.put("/{row_id}", response_model=RowResponse)
async def update_row(row_id: int, data: RowUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await RowCRUD.update(row_id, data, session)

@router.delete("/{row_id}")
async def delete_row(row_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await RowCRUD.delete(row_id, session)