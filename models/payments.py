from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from config.base import Base
from sqlalchemy.orm import relationship

class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    payments = relationship("Payment", back_populates="payment_method")


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=False)
    amount = Column(Integer, nullable=False)  # Сумма в копейках или минимальной единице валюты
    status = Column(String(50), nullable=False)  # Например, 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None))

    payment_method = relationship("PaymentMethod", back_populates="payments")
    ticket = relationship("Ticket", back_populates="payment", uselist=False)