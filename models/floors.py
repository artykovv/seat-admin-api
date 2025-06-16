from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.base import Base
from .projects import floor_projects

class Floor(Base):
    __tablename__ = "floors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Например, "Партер", "Амфитеатр"
    sections = relationship("Section", back_populates="floor")
    projects = relationship("Project", secondary=floor_projects, back_populates="floors")