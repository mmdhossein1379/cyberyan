from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProfileItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    linkedin_url: str | None = None
    industry: str | None = None
    job_title: str | None = None
    job_company_name: str | None = None
    location_name: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)


class SearchResponse(BaseModel):
    items: list[ProfileItem]
    total: int
    page: int
    page_size: int
    pages: int


class FilterOptions(BaseModel):
    skills: list[str]
    job_titles: list[str]
