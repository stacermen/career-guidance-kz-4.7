"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2026-05-10 07:30:00

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_init"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("education_level", sa.String(length=80), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=40), nullable=False, unique=True, index=True),
        sa.Column("title_ru", sa.String(length=200), nullable=False),
        sa.Column("title_en", sa.String(length=200), nullable=False),
        sa.Column("description_ru", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("order_num", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "test_id",
            sa.Integer(),
            sa.ForeignKey("tests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("order_num", sa.Integer(), nullable=False),
        sa.Column("text_ru", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=20), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.UniqueConstraint("test_id", "order_num", name="uq_questions_test_order"),
    )

    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "session_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("session_id", "question_id", name="uq_answers_session_q"),
    )

    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("raw_scores", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("traits", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "universities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name_ru", sa.String(length=200), nullable=False, index=True),
        sa.Column("name_en", sa.String(length=200), nullable=False),
        sa.Column("short_name", sa.String(length=40), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=False, index=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "specializations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "university_id",
            sa.Integer(),
            sa.ForeignKey("universities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("description_ru", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False, index=True),
        sa.Column(
            "grant_available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("tuition_cost", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "result_id",
            sa.Integer(),
            sa.ForeignKey("results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "specialization_id",
            sa.Integer(),
            sa.ForeignKey("specializations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("reason_ru", sa.Text(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("recommendations")
    op.drop_table("specializations")
    op.drop_table("universities")
    op.drop_table("results")
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("tests")
    op.drop_table("users")
