from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from services.projects import ProjectCRUD
from typing import List
from models import Project, ProjectDate, User
from auth.fastapi_users_instance import fastapi_users
from sqlalchemy.orm import selectinload, joinedload

from models import Row, Seat, SeatStatus, SeatProjectStatus, ProjectDate, Section, Project, Floor, floor_projects

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(data: ProjectCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await ProjectCRUD.create(data, session)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, session: AsyncSession = Depends(get_async_session)):
    return await ProjectCRUD.get(session, project_id)

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(session: AsyncSession = Depends(get_async_session)):
    return await ProjectCRUD.get(session)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, data: ProjectUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await ProjectCRUD.update(project_id, data, session)

@router.delete("/{project_id}")
async def delete_project(project_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(fastapi_users.current_user(active=True))):
    return await ProjectCRUD.delete(project_id, session)

@router.get("/seats/")
async def get_seats_by_project_date(
    project_id: int = Query(..., description="ID of the Project"),
    project_date_id: int = Query(..., description="ID of the ProjectDate"),
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Проверяем, существует ли Project
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # 2. Проверяем, существует ли ProjectDate и принадлежит ли она проекту
    result = await session.execute(
        select(ProjectDate).where(
            ProjectDate.id == project_date_id,
            ProjectDate.project_id == project_id
        )
    )
    project_date = result.scalar_one_or_none()
    if not project_date:
        raise HTTPException(status_code=404, detail=f"Project date with id {project_date_id} not found for project {project_id}")

    # 3. Загружаем этажи, связанные с проектом через floor_projects
    result = await session.execute(
        select(Floor)
        .join(floor_projects, floor_projects.c.floor_id == Floor.id)
        .where(floor_projects.c.project_id == project_id)
    )
    valid_floors = {floor.id for floor in result.scalars().all()}
    if not valid_floors:
        raise HTTPException(status_code=404, detail=f"No floors associated with project {project_id}")

    # 4. Загружаем все места с возможным статусом через outerjoin
    result = await session.execute(
        select(Seat, SeatProjectStatus.status_id.label("status_id"), SeatStatus.name.label("status_name"))
        .options(
            joinedload(Seat.row).joinedload(Row.section).joinedload(Section.floor),
            joinedload(Seat.category),
            selectinload(Seat.statuses).joinedload(SeatProjectStatus.status)
        )
        .outerjoin(
            SeatProjectStatus,
            (SeatProjectStatus.seat_id == Seat.id) &
            (SeatProjectStatus.project_date_id == project_date_id)
        )
        .outerjoin(SeatStatus, SeatStatus.id == SeatProjectStatus.status_id)
        .join(Row, Seat.row_id == Row.id)
        .join(Section, Row.section_id == Section.id)
        .join(Floor, Section.floor_id == Floor.id)
        .where(Floor.id.in_(valid_floors))
    )
    seats = result.unique().all()

    # 5. Группируем по этажам → секциям → рядам
    floor_map = {}
    for seat_data in seats:
        seat = seat_data.Seat
        status_id = seat_data.status_id
        status_name = seat_data.status_name

        row = seat.row
        section = row.section
        floor = section.floor
        category = seat.category

        floor_entry = floor_map.setdefault(floor.id, {
            "id": floor.id,
            "name": floor.name,
            "sections": {}
        })

        section_entry = floor_entry["sections"].setdefault(section.id, {
            "id": section.id,
            "name": section.name,
            "rows": {}
        })

        row_entry = section_entry["rows"].setdefault(row.id, {
            "id": row.id,
            "number": row.number,
            "seats": []
        })

        final_status = "free" if status_id is None or status_id == 1 else status_name

        row_entry["seats"].append({
            "id": seat.id,
            "number": seat.number,
            "gap_before": seat.gap_before,
            "gap_after": seat.gap_after,
            "category": {
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "price": str(category.price)
            },
            "status": final_status
        })

    # 6. Преобразуем в массив с сортировкой
    floors = []
    for floor in floor_map.values():
        sections = []
        for section in floor["sections"].values():
            rows = sorted(section["rows"].values(), key=lambda x: x["number"])
            section["rows"] = rows
            sections.append(section)
        floor["sections"] = sorted(sections, key=lambda x: x["id"])
        floors.append(floor)

    floors = sorted(floors, key=lambda x: x["id"])
    return floors

@router.get("/{project_id}/dates")
async def get_project_dates(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    # Проверяем, существует ли Project
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # Получаем все ProjectDate для проекта
    result = await session.execute(
        select(ProjectDate).where(ProjectDate.project_id == project_id)
    )
    project_dates = result.scalars().all()

    return [
        {
            "id": pd.id,
            "project_id": pd.project_id,
            "date": pd.date.isoformat()
        }
        for pd in project_dates
    ]