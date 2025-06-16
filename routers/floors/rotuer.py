from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from schemas.floors import FloorCreate, FloorUpdate, FloorResponse
from services.floors import FloorCRUD
from typing import List
from models import User
from auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/floors", tags=["floors"])

@router.post("/", response_model=FloorResponse)
async def create_floor(data: FloorCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await FloorCRUD.create(data, session)

@router.get("/{floor_id}", response_model=FloorResponse)
async def get_floor(floor_id: int, session: AsyncSession = Depends(get_async_session)):
    return await FloorCRUD.get(session, floor_id)

@router.get("/", response_model=List[FloorResponse])
async def get_floors(session: AsyncSession = Depends(get_async_session)):
    return await FloorCRUD.get(session)

@router.put("/{floor_id}", response_model=FloorResponse)
async def update_floor(floor_id: int, data: FloorUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await FloorCRUD.update(floor_id, data, session)

@router.delete("/{floor_id}")
async def delete_floor(floor_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await FloorCRUD.delete(floor_id, session)