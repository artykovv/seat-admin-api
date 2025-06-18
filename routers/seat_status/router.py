from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from schemas.seat_statuses import SeatStatusCreate, SeatStatusUpdate, SeatStatusResponse
from services.seat_statuses import SeatStatusCRUD
from typing import List
from models import User
from auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/seat-statuses", tags=["seat-statuses"])

@router.post("/", response_model=SeatStatusResponse)
async def create_seat_status(data: SeatStatusCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(is_superuser=True))):
    return await SeatStatusCRUD.create(data, session)

@router.get("/{status_id}", response_model=SeatStatusResponse)
async def get_seat_status(status_id: int, session: AsyncSession = Depends(get_async_session)):
    return await SeatStatusCRUD.get(session, status_id)

@router.get("/", response_model=List[SeatStatusResponse])
async def get_seat_statuses(session: AsyncSession = Depends(get_async_session)):
    return await SeatStatusCRUD.get(session)

@router.put("/{status_id}", response_model=SeatStatusResponse)
async def update_seat_status(status_id: int, data: SeatStatusUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(is_superuser=True))):
    return await SeatStatusCRUD.update(status_id, data, session)

@router.delete("/{status_id}")
async def delete_seat_status(status_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(is_superuser=True))):
    return await SeatStatusCRUD.delete(status_id, session)