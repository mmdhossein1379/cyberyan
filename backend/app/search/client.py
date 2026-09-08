from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from app.core.config import settings


es = AsyncElasticsearch(
    hosts=[settings.elasticsearch_url],
    request_timeout=30,
)