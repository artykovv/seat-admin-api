from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from config.base import Base
from .tickets import ticket_seats

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)  # Номер места внутри секции
    category_id = Column(Integer, ForeignKey("seat_categories.id"), default=1)
    category = relationship("SeatCategory", back_populates="seats")
    row_id = Column(Integer, ForeignKey("rows.id"))
    row = relationship("Row", back_populates="seats")
    gap_before = Column(Integer, default=0)  # Сколько пробелов ДО этого места
    gap_after = Column(Integer, default=0)   # Сколько пробелов ПОСЛЕ этого места
    statuses = relationship("SeatProjectStatus", back_populates="seat", cascade="all, delete-orphan")
    tickets = relationship(
        "Ticket",
        secondary=ticket_seats,
        back_populates="seats",
        primaryjoin="and_(Seat.id == ticket_seats.c.seat_id, ticket_seats.c.project_date_id == Ticket.project_date_id)"
    )

class SeatCategory(Base):
    __tablename__ = "seat_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Например, "VIP", "Ближес", "Стандарт"
    color = Column(String, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    seats = relationship("Seat", back_populates="category")

class SeatStatus(Base):
    __tablename__ = "seat_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # Например, "free", "booked", "sold"
    color = Column(String, nullable=True)
    description = Column(String, nullable=True)
    seat_project_statuses = relationship("SeatProjectStatus", back_populates="status")

class SeatProjectStatus(Base):
    __tablename__ = "seat_project_statuses"
    id = Column(Integer, primary_key=True)
    project_date_id = Column(Integer, ForeignKey("project_dates.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("seat_statuses.id"), nullable=False)

    seat = relationship("Seat", back_populates="statuses")
    project_date = relationship("ProjectDate", back_populates="seat_statuses")
    status = relationship("SeatStatus")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None), nullable=False)

    __table_args__ = (
        UniqueConstraint("project_date_id", "seat_id", name="uq_project_date_seat"),
    )