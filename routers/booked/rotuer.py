from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from pydantic import BaseModel
from typing import List
from datetime import datetime
from config.database import get_async_session
from auth.fastapi_users_instance import fastapi_users
from models import Client, Ticket, Payment, PaymentMethod, Seat, SeatProjectStatus, SeatStatus, ProjectDate, Project, ticket_seats, User

router = APIRouter(prefix="/booking", tags=["booked"])

class CreateTicketRequest(BaseModel):
    project_id: int
    project_date_id: int
    seat_ids: List[int]
    client_full_name: str
    client_phone_number: str
    payment_method_code: str  # Например, 'card', 'cash'
    amount: int  # Сумма в копейках

@router.post("/tickets")
async def create_ticket(
    request: CreateTicketRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(active=True)),
):
    # 1. Проверяем Project и ProjectDate
    result = await session.execute(
        select(Project).where(Project.id == request.project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await session.execute(
        select(ProjectDate).where(
            ProjectDate.id == request.project_date_id,
            ProjectDate.project_id == request.project_id
        )
    )
    project_date = result.scalar_one_or_none()
    if not project_date:
        raise HTTPException(status_code=404, detail="Project date not found")

    # 2. Проверяем PaymentMethod
    result = await session.execute(
        select(PaymentMethod).where(PaymentMethod.code == request.payment_method_code, PaymentMethod.is_active == True)
    )
    payment_method = result.scalar_one_or_none()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found or inactive")

    # 3. Проверяем Seat IDs
    result = await session.execute(
        select(Seat.id).where(Seat.id.in_(request.seat_ids))
    )
    existing_seat_ids = {row[0] for row in result.fetchall()}
    invalid_seat_ids = set(request.seat_ids) - existing_seat_ids
    if invalid_seat_ids:
        raise HTTPException(status_code=400, detail=f"Invalid seat IDs: {list(invalid_seat_ids)}")

    # 4. Проверяем, что места свободны
    result = await session.execute(
        select(SeatStatus).where(SeatStatus.name == "booked")
    )
    booked_status = result.scalar_one_or_none()
    if not booked_status:
        raise HTTPException(status_code=404, detail="Seat status 'booked' not found")

    result = await session.execute(
        select(SeatProjectStatus.seat_id)
        .where(
            SeatProjectStatus.project_date_id == request.project_date_id,
            SeatProjectStatus.seat_id.in_(request.seat_ids),
            SeatProjectStatus.status_id != booked_status.id
        )
    )
    already_booked_seats = {row[0] for row in result.fetchall()}
    if already_booked_seats:
        raise HTTPException(status_code=400, detail=f"Seats already booked: {list(already_booked_seats)}")

    # 5. Находим или создаём клиента
    result = await session.execute(
        select(Client).where(Client.phone_number == request.client_phone_number)
    )
    client = result.scalar_one_or_none()
    if not client:
        client = Client(
            full_name=request.client_full_name,
            phone_number=request.client_phone_number
        )
        session.add(client)
        await session.flush()

    # 6. Создаём оплату
    payment = Payment(
        payment_method_id=payment_method.id,
        amount=request.amount,
        status="completed"  # Предполагаем, что оплата успешна
    )
    session.add(payment)
    await session.flush()

    # 7. Создаём билет
    ticket = Ticket(
        client_id=client.id,
        project_id=request.project_id,
        project_date_id=request.project_date_id,
        payment_id=payment.id
    )
    session.add(ticket)
    await session.flush()

    # 8. Привязываем места к билету и обновляем статусы
    for seat_id in request.seat_ids:
        # Добавляем в ticket_seats
        await session.execute(
            insert(ticket_seats).values(
                ticket_id=ticket.id,
                seat_id=seat_id,
                project_date_id=request.project_date_id
            )
        )
        # Обновляем или создаём SeatProjectStatus
        result = await session.execute(
            select(SeatProjectStatus)
            .where(
                SeatProjectStatus.project_date_id == request.project_date_id,
                SeatProjectStatus.seat_id == seat_id
            )
        )
        existing_status = result.scalar_one_or_none()
        if existing_status:
            await session.execute(
                update(SeatProjectStatus)
                .where(
                    SeatProjectStatus.project_date_id == request.project_date_id,
                    SeatProjectStatus.seat_id == seat_id
                )
                .values(
                    status_id=booked_status.id,
                    updated_at=datetime.now()
                )
            )
        else:
            await session.execute(
                insert(SeatProjectStatus).values(
                    project_date_id=request.project_date_id,
                    seat_id=seat_id,
                    status_id=booked_status.id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )

    await session.commit()

    return {
        "message": "Ticket created successfully",
        "ticket_id": ticket.id,
        "client_id": client.id,
        "seat_ids": request.seat_ids
    }