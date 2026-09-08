"""create profiles table

Revision ID: 0001
Revises:
Create Date: 2026-09-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("job_title", sa.String(length=255), nullable=True),
        sa.Column("job_company_name", sa.String(length=255), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("education", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("experience", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("search_text", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_profiles_job_title", "profiles", ["job_title"])
    op.create_index("ix_profiles_industry", "profiles", ["industry"])
    op.execute("CREATE INDEX ix_profiles_skills_gin ON profiles USING GIN (skills)")
    op.execute(
        "CREATE INDEX ix_profiles_search_fts ON profiles "
        "USING GIN (to_tsvector('simple', search_text))"
    )


def downgrade() -> None:
    op.drop_table("profiles")
