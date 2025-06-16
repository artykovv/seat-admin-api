from datetime import datetime, timedelta, timezone
from config.base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship

ticket_seats = Table(
    "ticket_seats",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey("tickets.id"), primary_key=True),
    Column("seat_id", Integer, ForeignKey("seats.id"), primary_key=True),
    Column("project_date_id", Integer, ForeignKey("project_dates.id"), primary_key=True)
)

class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project_date_id = Column(Integer, ForeignKey('project_dates.id'), nullable=False)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=True)  # Может быть NULL, если оплата в процессе
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None))
    client = relationship("Client", back_populates="tickets")
    project = relationship("Project")
    project_date = relationship("ProjectDate")
    payment = relationship("Payment", back_populates="ticket")
    seats = relationship(
        "Seat",
        secondary=ticket_seats,
        back_populates="tickets",
        primaryjoin="and_(Ticket.id == ticket_seats.c.ticket_id, Ticket.project_date_id == ticket_seats.c.project_date_id)"
    )