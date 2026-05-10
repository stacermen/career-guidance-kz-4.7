"""Pydantic v2 schemas exposed by the API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --------------------------- session / onboarding ---------------------------


class SessionCreate(BaseModel):
    name: str | None = None
    age: int | None = None
    education_level: str | None = None


class SessionOut(ORM):
    session_id: uuid.UUID
    name: str | None
    age: int | None
    education_level: str | None


# --------------------------- tests / questions ------------------------------


class QuestionOut(ORM):
    id: int
    order_num: int
    text_ru: str
    question_type: str
    options: dict[str, Any] | None = None


class TestOut(ORM):
    id: int
    slug: str
    title_ru: str
    title_en: str
    description_ru: str
    category: str
    order_num: int
    questions: list[QuestionOut]


# --------------------------- answers ----------------------------------------


class AnswerIn(BaseModel):
    question_id: int
    value: int | str | float | list[int] | list[str] | dict[str, Any]


class AnswerBatchIn(BaseModel):
    session_id: uuid.UUID
    answers: list[AnswerIn]


class AnswerBatchOut(BaseModel):
    saved: int


# --------------------------- analysis ---------------------------------------


class AnalyzeIn(BaseModel):
    session_id: uuid.UUID


class CareerPath(BaseModel):
    title_ru: str
    match_score: float = Field(ge=0, le=100)
    why_match: str
    specialization_categories: list[str]


class AIAnalysis(BaseModel):
    personality_summary: str
    strengths: list[str]
    growth_areas: list[str]
    ideal_work_environment: str
    career_paths: list[CareerPath]
    study_tips: str
    motivational_message: str


class UniversityOut(ORM):
    id: int
    name_ru: str
    name_en: str
    short_name: str | None
    city: str
    website: str | None
    logo_url: str | None


class SpecializationOut(ORM):
    id: int
    code: str
    name_ru: str
    name_en: str
    description_ru: str
    category: str
    grant_available: bool
    tuition_cost: int
    university: UniversityOut


class RecommendationOut(ORM):
    id: int
    match_score: float
    reason_ru: str
    rank: int
    specialization: SpecializationOut


class ResultsOut(BaseModel):
    session_id: uuid.UUID
    created_at: datetime
    raw_scores: dict[str, Any]
    traits: dict[str, Any] | None
    analysis: AIAnalysis
    recommendations: list[RecommendationOut]


# --------------------------- chat -------------------------------------------


class ChatMessageIn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatIn(BaseModel):
    session_id: uuid.UUID
    messages: list[ChatMessageIn]


# --------------------------- universities listing ---------------------------


class UniversityListOut(BaseModel):
    items: list[UniversityOut]


class SpecializationListItem(SpecializationOut):
    pass


class SpecializationListOut(BaseModel):
    items: list[SpecializationListItem]
