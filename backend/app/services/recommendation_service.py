"""Match Claude's recommended career paths to the seeded specialization catalogue."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Recommendation, Specialization
from app.schemas.schemas import AIAnalysis


async def build_recommendations(
    db: AsyncSession,
    result_id: int,
    analysis: AIAnalysis,
    limit: int = 24,
) -> list[Recommendation]:
    """For each Claude career path, select up to N matching specializations.

    The match score for each specialization is the parent path's `match_score`
    minus a small per-rank decay so cards within a path are ordered.
    """
    # Eager-load the university so callers can serialize without extra queries.
    stmt = select(Specialization).options(selectinload(Specialization.university))
    result = await db.execute(stmt)
    all_specs: Sequence[Specialization] = result.scalars().all()

    seen_ids: set[int] = set()
    recommendations: list[Recommendation] = []
    rank = 1
    for path in analysis.career_paths:
        path_categories = {c.strip() for c in path.specialization_categories if c.strip()}
        if not path_categories:
            continue
        # Take up to 3 specs per category in the path, prioritising grant-available
        per_path: list[Specialization] = []
        for spec in all_specs:
            if spec.id in seen_ids:
                continue
            if spec.category in path_categories:
                per_path.append(spec)
        per_path.sort(key=lambda s: (not s.grant_available, s.tuition_cost))
        for offset, spec in enumerate(per_path[:6]):
            seen_ids.add(spec.id)
            decay = offset * 0.5
            score = max(0.0, min(100.0, path.match_score - decay))
            rec = Recommendation(
                result_id=result_id,
                specialization_id=spec.id,
                match_score=round(score, 1),
                reason_ru=path.why_match,
                rank=rank,
            )
            db.add(rec)
            recommendations.append(rec)
            rank += 1
            if len(recommendations) >= limit:
                break
        if len(recommendations) >= limit:
            break

    await db.flush()
    return recommendations
