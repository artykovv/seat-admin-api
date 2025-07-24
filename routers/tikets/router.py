from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, func, select
from config.database import get_async_session
from models import Ticket, Client, Project, ProjectDate, Payment, Seat, Row, Section, SeatProjectStatus, ticket_seats, User
from typing import Optional
from sqlalchemy.orm import joinedload
from auth.fastapi_users_instance import fastapi_users
from schemas.tikets import TicketResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/search", response_model=list[TicketResponse])
async def search_tickets(
    phone_number: Optional[str] = Query(None),
    ticket_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    project_date_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    query = (
        select(Ticket)
        .join(Client)
        .join(Project)
        .join(ProjectDate)
        .outerjoin(Payment)
        .options(
            joinedload(Ticket.client),
            joinedload(Ticket.project),
            joinedload(Ticket.project_date),
            joinedload(Ticket.payment),
            joinedload(Ticket.seats)
                .joinedload(Seat.row)
                .joinedload(Row.section)
                .joinedload(Section.floor),
            joinedload(Ticket.seats).joinedload(Seat.category)
        )
    )

    if phone_number:
        query = query.filter(Client.phone_number.ilike(f"%{phone_number}%"))
    if ticket_id:
        query = query.filter(Ticket.id == ticket_id)
    if project_id:
        query = query.filter(Ticket.project_id == project_id)
    if project_date_id:
        query = query.filter(Ticket.project_date_id == project_date_id)

    result = await session.execute(query)
    tickets = result.unique().scalars().all()

    response = []
    for ticket in tickets:
        seats_info = [
            {
                "floor_name": seat.row.section.floor.name if seat.row and seat.row.section and seat.row.section.floor else "N/A",
                "row_number": seat.row.number if seat.row else "N/A",
                "seat_number": seat.number,
                "seat_id": seat.id,
                "price": float(seat.category.price) if seat.category else 0.0
            }
            for seat in ticket.seats
        ]
        response.append({
            "id": ticket.id,
            "client_full_name": ticket.client.full_name,
            "client_phone_number": ticket.client.phone_number,
            "project_name": ticket.project.name,
            "project_id": ticket.project_id,
            "project_date_id": ticket.project_date_id,
            "project_date": ticket.project_date.date.isoformat(),
            "payment_status": ticket.payment.status if ticket.payment else "Ожидает оплаты",
            "amount": ticket.payment.amount if ticket.payment else None,
            "seats": seats_info
        })

    return response

# 
@router.delete("/tiket")
async def delete_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    # Найти билет
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Получаем связанные места и project_date_id
    seat_rows = await session.execute(
        select(ticket_seats.c.seat_id, ticket_seats.c.project_date_id)
        .where(ticket_seats.c.ticket_id == ticket_id)
    )
    rows = seat_rows.all()
    seat_ids = [r[0] for r in rows]
    project_date_ids = list(set(r[1] for r in rows))

    # Удаляем сам билет (удалит и из ticket_seats)
    await session.delete(ticket)

    # Удаляем статусы мест по каждому project_date_id
    for pd_id in project_date_ids:
        await session.execute(
            delete(SeatProjectStatus).where(
                SeatProjectStatus.project_date_id == pd_id,
                SeatProjectStatus.seat_id.in_(seat_ids)
            )
        )

    await session.commit()
    return {
        "massage": "Успешно удалено"
    }

@router.delete("/tikets/seats")
async def remove_seats_from_ticket(
    ticket_id: int, 
    seat_ids: list[int], 
    project_date_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    # Проверка на существование билета
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Удаляем связи из ticket_seats
    await session.execute(
        delete(ticket_seats).where(
            ticket_seats.c.ticket_id == ticket_id,
            ticket_seats.c.project_date_id == project_date_id,
            ticket_seats.c.seat_id.in_(seat_ids)
        )
    )

    # Удаляем статусы мест
    await session.execute(
        delete(SeatProjectStatus).where(
            SeatProjectStatus.project_date_id == project_date_id,
            SeatProjectStatus.seat_id.in_(seat_ids)
        )
    )

    await session.commit()
    return {
        "massage": "Успешно удалено"
    }