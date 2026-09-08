from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.profile import FilterOptions, SearchResponse
from app.services.search import get_filter_options, search_profiles

router = APIRouter(prefix="/profiles", tags=["profiles"])
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/search", response_model=SearchResponse)
async def search(
    db: DbSession,
    q: str | None = Query(default=None, max_length=200, description="Free-text keyword"),
    skill: list[str] = Query(default_factory=list, description="Repeat to require multiple skills"),
    job_title: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
) -> SearchResponse:
    result = await search_profiles(
        keyword=q,
        skills=skill,
        job_title=job_title,
        page=page,
        page_size=page_size,
    )

    return result



@router.get("/filters")
async def filters():
    return await get_filter_options()