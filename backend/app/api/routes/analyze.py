"""POST /api/analyze — runs scoring → Claude → recommendations and persists everything."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import Answer, Question, Recommendation, Result, Test, User
from app.schemas.schemas import AnalyzeIn, ResultsOut
from app.services import ai_service, recommendation_service
from app.services.scoring_service import holland_code_letters, score_all

router = APIRouter()


async def _compute_scores(db: AsyncSession, session_id) -> tuple[dict, dict]:
    # Fetch all answers + their question metadata + parent test slug in one go.
    stmt = (
        select(Answer, Question, Test)
        .join(Question, Question.id == Answer.question_id)
        .join(Test, Test.id == Question.test_id)
        .where(Answer.session_id == session_id)
    )
    res = await db.execute(stmt)
    grouped: dict[str, list[dict]] = {}
    for answer, question, test in res.all():
        grouped.setdefault(test.slug, []).append(
            {
                "value": answer.value,
                "question_type": question.question_type,
                "meta": question.meta or {},
            }
        )
    scores = score_all(grouped)
    traits = {
        "holland_code": holland_code_letters(scores["holland"]) if scores["holland"] else "",
    }
    return scores, traits


@router.post("/analyze", response_model=ResultsOut)
async def analyze(payload: AnalyzeIn, db: AsyncSession = Depends(get_db)) -> ResultsOut:
    user_res = await db.execute(select(User).where(User.session_id == payload.session_id))
    user = user_res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Session not found")

    scores, traits = await _compute_scores(db, payload.session_id)
    if not any(any(scores[k].values()) for k in scores):
        raise HTTPException(status_code=400, detail="No answers found for this session")

    analysis = await ai_service.analyze(scores, user_name=user.name)

    # Replace any prior result for this session.
    prior = await db.execute(select(Result).where(Result.session_id == payload.session_id))
    prior_result = prior.scalar_one_or_none()
    if prior_result is not None:
        await db.execute(
            delete(Recommendation).where(Recommendation.result_id == prior_result.id)
        )
        await db.delete(prior_result)
        await db.flush()

    result = Result(
        session_id=payload.session_id,
        raw_scores=scores,
        ai_analysis=analysis.model_dump_json(),
        traits=traits,
    )
    db.add(result)
    await db.flush()

    await recommendation_service.build_recommendations(db, result.id, analysis)
    await db.commit()

    # Re-fetch with the relationships needed for the response.
    from app.models import Specialization

    full = await db.execute(
        select(Result)
        .where(Result.id == result.id)
        .options(
            selectinload(Result.recommendations)
            .selectinload(Recommendation.specialization)
            .selectinload(Specialization.university)
        )
    )
    res_obj = full.scalar_one()

    return ResultsOut(
        session_id=res_obj.session_id,
        created_at=res_obj.created_at,
        raw_scores=res_obj.raw_scores,
        traits=res_obj.traits,
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
            for r in res_obj.recommendations
        ],
    )


@router.get("/analyze/{session_id}/scores")
async def debug_scores(session_id, db: AsyncSession = Depends(get_db)) -> dict:
    """Helper for the frontend to peek at raw scores without re-running Claude."""
    scores, traits = await _compute_scores(db, session_id)
    return {"scores": scores, "traits": traits, "code": json.dumps(traits)}
