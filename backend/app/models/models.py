"""SQLAlchemy 2.0 ORM models for the career guidance platform."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """Anonymous user identified by a session UUID."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Test(Base):
    """A single psychometric test module."""

    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    title_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    title_en: Mapped[str] = mapped_column(String(200), nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    questions: Mapped[list[Question]] = relationship(
        "Question", back_populates="test", cascade="all, delete-orphan", order_by="Question.order_num"
    )


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("test_id", "order_num", name="uq_questions_test_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)
    text_ru: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSONB on Postgres; the `JSON` type maps to JSONB automatically with the asyncpg driver.
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Free-form metadata for scoring (e.g. trait, reverse-scored flag, weight).
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    test: Mapped[Test] = relationship("Test", back_populates="questions")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_answers_session_q"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    # `value` is stored as JSON to allow scalars (1-5), strings, or arrays (rankings).
    value: Mapped[dict | list | str | int | float | None] = mapped_column(JSON, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    raw_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    traits: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    recommendations: Mapped[list[Recommendation]] = relationship(
        "Recommendation",
        back_populates="result",
        cascade="all, delete-orphan",
        order_by="Recommendation.rank",
    )


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    city: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    specializations: Mapped[list[Specialization]] = relationship(
        "Specialization", back_populates="university", cascade="all, delete-orphan"
    )


class Specialization(Base):
    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int] = mapped_column(
        ForeignKey("universities.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    grant_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tuition_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    university: Mapped[University] = relationship("University", back_populates="specializations")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_id: Mapped[int] = mapped_column(
        ForeignKey("results.id", ondelete="CASCADE"), nullable=False
    )
    specialization_id: Mapped[int] = mapped_column(
        ForeignKey("specializations.id", ondelete="CASCADE"), nullable=False
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason_ru: Mapped[str] = mapped_column(Text, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    result: Mapped[Result] = relationship("Result", back_populates="recommendations")
    specialization: Mapped[Specialization] = relationship("Specialization")
