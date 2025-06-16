from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, DateTime, String
from datetime import datetime, timezone, timedelta
from config.base import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'users'
    
    name = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    register_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone(timedelta(hours=3))).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone(timedelta(hours=3))).replace(tzinfo=None), onupdate=datetime.now(timezone(timedelta(hours=3))).replace(tzinfo=None), nullable=False)
    

