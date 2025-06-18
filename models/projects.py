from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from config.base import Base

floor_projects = Table(
    "floor_projects",
    Base.metadata,
    Column("floor_id", Integer, ForeignKey("floors.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True)
)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    poster_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    dates = relationship("ProjectDate", back_populates="project")
    floors = relationship("Floor", secondary=floor_projects, back_populates="projects")

class ProjectDate(Base):
    __tablename__ = "project_dates"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    date = Column(Date, nullable=False)

    project = relationship("Project", back_populates="dates")
    seat_statuses = relationship("SeatProjectStatus", back_populates="project_date")

    __table_args__ = (
        UniqueConstraint("project_id", "date", name="uq_project_date"),
    )