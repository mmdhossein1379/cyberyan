from __future__ import annotations

from typing import Any

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    industry: Mapped[str | None] = mapped_column(String(255))
    job_title: Mapped[str | None] = mapped_column(String(255))
    job_company_name: Mapped[str | None] = mapped_column(String(255))
    location_name: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    education: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    experience: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    search_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
