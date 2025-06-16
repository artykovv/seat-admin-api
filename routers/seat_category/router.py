from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from schemas.seat_categories import SeatCategoryCreate, SeatCategoryUpdate, SeatCategoryResponse
from services.seat_categories import SeatCategoryCRUD
from typing import List
from models import User
from auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/seat-categories", tags=["seat-categories"])

@router.post("/", response_model=SeatCategoryResponse)
async def create_seat_category(data: SeatCategoryCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await SeatCategoryCRUD.create(data, session)

@router.get("/{category_id}", response_model=SeatCategoryResponse)
async def get_seat_category(category_id: int, session: AsyncSession = Depends(get_async_session)):
    return await SeatCategoryCRUD.get(session, category_id)

@router.get("/", response_model=List[SeatCategoryResponse])
async def get_seat_categories(session: AsyncSession = Depends(get_async_session)):
    return await SeatCategoryCRUD.get(session)

@router.put("/{category_id}", response_model=SeatCategoryResponse)
async def update_seat_category(category_id: int, data: SeatCategoryUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await SeatCategoryCRUD.update(category_id, data, session)

@router.delete("/{category_id}")
async def delete_seat_category(category_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await SeatCategoryCRUD.delete(category_id, session)