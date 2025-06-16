from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models import PaymentMethod, Payment  # ваш импорт моделей


class PaymentMethodCRUD:
    @staticmethod
    async def create(session: AsyncSession, name: str, code: str, is_active: bool = True) -> PaymentMethod:
        payment_method = PaymentMethod(name=name, code=code, is_active=is_active)
        session.add(payment_method)
        await session.commit()
        await session.refresh(payment_method)
        return payment_method

    @staticmethod
    async def get(session: AsyncSession) -> Optional[PaymentMethod]:
        result = await session.execute(select(PaymentMethod))
        return result.scalars().all()


    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[PaymentMethod]:
        result = await session.execute(select(PaymentMethod).where(PaymentMethod.id == id))
        return result.scalars().first()

    @staticmethod
    async def get_by_code(session: AsyncSession, code: str) -> Optional[PaymentMethod]:
        result = await session.execute(select(PaymentMethod).where(PaymentMethod.code == code))
        return result.scalars().first()

    @staticmethod
    async def update(session: AsyncSession, id: int, **kwargs) -> Optional[PaymentMethod]:
        # kwargs могут быть: name, code, is_active
        await session.execute(update(PaymentMethod).where(PaymentMethod.id == id).values(**kwargs))
        await session.commit()
        return await PaymentMethodCRUD.get_by_id(session, id)

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        result = await session.execute(delete(PaymentMethod).where(PaymentMethod.id == id))
        await session.commit()
        return result.rowcount > 0


class PaymentCRUD:
    @staticmethod
    async def create(session: AsyncSession, payment_method_id: int, amount: int, status: str) -> Payment:
        payment = Payment(payment_method_id=payment_method_id, amount=amount, status=status)
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Payment]:
        result = await session.execute(select(Payment).where(Payment.id == id))
        return result.scalars().first()

    @staticmethod
    async def update(session: AsyncSession, id: int, **kwargs) -> Optional[Payment]:
        # kwargs могут быть: payment_method_id, amount, status
        await session.execute(update(Payment).where(Payment.id == id).values(**kwargs))
        await session.commit()
        return await PaymentCRUD.get_by_id(session, id)

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        result = await session.execute(delete(Payment).where(Payment.id == id))
        await session.commit()
        return result.rowcount > 0