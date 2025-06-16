from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from config.base import Base

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)  # ФИО
    phone_number = Column(String(20), nullable=False, unique=True)  # Номер телефона
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None))

    tickets = relationship("Ticket", back_populates="client")