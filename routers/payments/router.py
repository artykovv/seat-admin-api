from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from services.payments import PaymentCRUD, PaymentMethodCRUD
from models import User
from auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/payment-methods/")
async def create_payment_method(name: str, code: str, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    pm = await PaymentMethodCRUD.create(session, name, code)
    return pm

@router.get("/payment-methods")
async def get_payment_methods(session: AsyncSession = Depends(get_async_session)):
    pm = await PaymentMethodCRUD.get(session)
    return pm

@router.get("/{payment_id}")
async def read_payment(payment_id: int, session: AsyncSession = Depends(get_async_session)):
    payment = await PaymentCRUD.get_by_id(session, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment