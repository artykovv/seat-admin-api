from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from config.base import Base

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, ForeignKey("floors.id"))
    name = Column(String, nullable=False)  # Например, "Секция 1-14", "Проход 14-15"
    floor = relationship("Floor", back_populates="sections")
    rows = relationship("Row", back_populates="section")