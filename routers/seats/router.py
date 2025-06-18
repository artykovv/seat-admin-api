from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from schemas.seats import SeatCreate, SeatUpdate, SeatResponse
from services.seat import SeatCRUD
from typing import List
from models import User
from auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/seats", tags=["seats"])

@router.post("/", response_model=SeatResponse)
async def create_seat(data: SeatCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(is_superuser=True))):
    return await SeatCRUD.create(data, session)

@router.get("/{seat_id}", response_model=SeatResponse)
async def get_seat(seat_id: int, session: AsyncSession = Depends(get_async_session)):
    return await SeatCRUD.get(session, seat_id)

@router.get("/", response_model=List[SeatResponse])
async def get_seats(session: AsyncSession = Depends(get_async_session)):
    return await SeatCRUD.get(session)

@router.put("/{seat_id}", response_model=SeatResponse)
async def update_seat(seat_id: int, data: SeatUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(is_superuser=True))):
    return await SeatCRUD.update(seat_id, data, session)

@router.delete("/{seat_id}")
async def delete_seat(seat_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(is_superuser=True))):
    return await SeatCRUD.delete(seat_id, session)