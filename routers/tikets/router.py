from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.database import get_async_session
from models import Ticket, Client, Project, ProjectDate, Payment, Seat, Row, Section
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/tickets", tags=["Tickets"])
class TicketResponse(BaseModel):
    id: int
    client_full_name: str
    client_phone_number: str
    project_name: str
    project_id: int
    project_date_id: int
    project_date: str
    payment_status: Optional[str]
    amount: Optional[int]
    seats: list[dict]

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