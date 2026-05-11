from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import Test
from app.schemas.schemas import TestOut

router = APIRouter()


@router.get("/tests", response_model=list[TestOut])
async def list_tests(db: AsyncSession = Depends(get_db)) -> list[TestOut]:
    stmt = (
        select(Test)
        .options(selectinload(Test.questions))
        .order_by(Test.order_num)
    )
    res = await db.execute(stmt)
    tests = res.scalars().all()
    return [TestOut.model_validate(t) for t in tests]
