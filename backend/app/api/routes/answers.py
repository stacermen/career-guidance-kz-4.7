from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import Answer
from app.schemas.schemas import AnswerBatchIn, AnswerBatchOut

router = APIRouter()


@router.post("/answers", response_model=AnswerBatchOut)
async def save_answers(payload: AnswerBatchIn, db: AsyncSession = Depends(get_db)) -> AnswerBatchOut:
    if not payload.answers:
        return AnswerBatchOut(saved=0)

    rows = [
        {
            "session_id": payload.session_id,
            "question_id": a.question_id,
            "value": a.value,
        }
        for a in payload.answers
    ]
    stmt = pg_insert(Answer).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["session_id", "question_id"],
        set_={"value": stmt.excluded.value},
    )
    await db.execute(stmt)
    await db.commit()

    # Count distinct answers persisted (helps the client show progress).
    res = await db.execute(
        select(Answer).where(Answer.session_id == payload.session_id)
    )
    return AnswerBatchOut(saved=len(res.scalars().all()))
