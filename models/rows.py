from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from config.base import Base

class Row(Base):
    __tablename__ = "rows"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"))
    section = relationship("Section", back_populates="rows")
    seats = relationship("Seat", back_populates="row")