from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import Specialization, University
from app.schemas.schemas import SpecializationListOut, UniversityListOut

router = APIRouter()


@router.get("/universities", response_model=UniversityListOut)
async def list_universities(
    city: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> UniversityListOut:
    stmt = select(University).order_by(University.name_ru)
    if city and city.lower() != "all":
        stmt = stmt.where(University.city == city)
    res = await db.execute(stmt)
    items = res.scalars().all()
    return UniversityListOut(items=items)


@router.get("/specializations", response_model=SpecializationListOut)
async def list_specializations(
    city: str | None = Query(default=None),
    category: str | None = Query(default=None),
    university_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SpecializationListOut:
    stmt = (
        select(Specialization)
        .options(selectinload(Specialization.university))
        .order_by(Specialization.name_ru)
    )
    if city and city.lower() != "all":
        stmt = stmt.where(Specialization.university.has(University.city == city))
    if category and category.lower() != "all":
        stmt = stmt.where(Specialization.category == category)
    if university_id:
        stmt = stmt.where(Specialization.university_id == university_id)
    res = await db.execute(stmt)
    items = res.scalars().all()
    return SpecializationListOut(items=items)
