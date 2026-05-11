import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import Recommendation, Result, Specialization, User
from app.schemas.schemas import AIAnalysis, ResultsOut
from app.services import pdf_service

router = APIRouter()


async def _load_full_result(db: AsyncSession, session_id: uuid.UUID) -> tuple[Result | None, User | None]:
    stmt = (
        select(Result)
        .where(Result.session_id == session_id)
        .options(
            selectinload(Result.recommendations)
            .selectinload(Recommendation.specialization)
            .selectinload(Specialization.university)
        )
    )
    res = await db.execute(stmt)
    result = res.scalar_one_or_none()
    user_res = await db.execute(select(User).where(User.session_id == session_id))
    user = user_res.scalar_one_or_none()
    return result, user


@router.get("/results/{session_id}", response_model=ResultsOut)
async def get_results(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ResultsOut:
    result, _ = await _load_full_result(db, session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Results not found")
    analysis = AIAnalysis.model_validate_json(result.ai_analysis or "{}")
    return ResultsOut(
        session_id=result.session_id,
        created_at=result.created_at,
        raw_scores=result.raw_scores,
        traits=result.traits,
        analysis=analysis,
        recommendations=[
            {
                "id": r.id,
                "match_score": r.match_score,
                "reason_ru": r.reason_ru,
                "rank": r.rank,
                "specialization": {
                    "id": r.specialization.id,
                    "code": r.specialization.code,
                    "name_ru": r.specialization.name_ru,
                    "name_en": r.specialization.name_en,
                    "description_ru": r.specialization.description_ru,
                    "category": r.specialization.category,
                    "grant_available": r.specialization.grant_available,
                    "tuition_cost": r.specialization.tuition_cost,
                    "university": {
                        "id": r.specialization.university.id,
                        "name_ru": r.specialization.university.name_ru,
                        "name_en": r.specialization.university.name_en,
                        "short_name": r.specialization.university.short_name,
                        "city": r.specialization.university.city,
                        "website": r.specialization.university.website,
                        "logo_url": r.specialization.university.logo_url,
                    },
                },
            }
            for r in result.recommendations
        ],
    )


@router.get("/results/{session_id}/pdf")
async def get_results_pdf(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Response:
    result, user = await _load_full_result(db, session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Results not found")
    analysis = AIAnalysis.model_validate(json.loads(result.ai_analysis or "{}"))
    pdf_bytes = pdf_service.render_results_pdf(
        user_name=user.name if user else None,
        raw_scores=result.raw_scores,
        analysis=analysis,
        recommendations=result.recommendations,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="career-guidance-{session_id}.pdf"'
        },
    )
