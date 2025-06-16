from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Union
from schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from models import Project

class ProjectCRUD:
    @staticmethod
    async def create(data: ProjectCreate, session: AsyncSession) -> ProjectResponse:
        project = Project(**data.dict())
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return ProjectResponse.from_orm(project)

    @staticmethod
    async def get(session: AsyncSession, project_id: int = None) -> Union[List[ProjectResponse], ProjectResponse]:
        if project_id:
            stmt = select(Project).where(Project.id == project_id)
            result = await session.execute(stmt)
            project = result.scalars().first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            return ProjectResponse.from_orm(project)
        stmt = select(Project)
        result = await session.execute(stmt)
        return [ProjectResponse.from_orm(p) for p in result.scalars().all()]

    @staticmethod
    async def update(project_id: int, data: ProjectUpdate, session: AsyncSession) -> ProjectResponse:
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(project, key, value)
        await session.commit()
        await session.refresh(project)
        return ProjectResponse.from_orm(project)

    @staticmethod
    async def delete(project_id: int, session: AsyncSession) -> dict:
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await session.delete(project)
        await session.commit()
        return {"message": "Project deleted successfully"}