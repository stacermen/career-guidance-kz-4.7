"""Streaming SSE chat endpoint backed by Claude."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.database import get_db
from app.models import Result
from app.schemas.schemas import ChatIn
from app.services import ai_service

router = APIRouter()


@router.post("/chat")
async def chat(payload: ChatIn, db: AsyncSession = Depends(get_db)) -> EventSourceResponse:
    res = await db.execute(select(Result).where(Result.session_id == payload.session_id))
    result = res.scalar_one_or_none()
    scores = result.raw_scores if result else None
    summary = result.ai_analysis if result else None

    history = [{"role": m.role, "content": m.content} for m in payload.messages]

    async def event_generator():
        async for chunk in ai_service.chat_stream(scores, summary, history):
            yield {"event": "token", "data": chunk}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
