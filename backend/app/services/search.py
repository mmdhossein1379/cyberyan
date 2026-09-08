from __future__ import annotations

from math import ceil

from elasticsearch import (
    NotFoundError,
    ApiError,
    ConnectionError as ElasticsearchConnectionError,
)

from app.core.config import settings
from app.search.client import es


FULL_TEXT_FIELDS = [
    "full_name^6",
    "job_title^5",
    "skills^5",
    "job_company_name^3",
    "industry^2",
    "location_name^2",
    "summary",
    "search_text",
]


AUTOCOMPLETE_FIELDS = [
    "full_name.autocomplete^6",
    "job_title.autocomplete^5",
    "skills.autocomplete^5",
    "job_company_name.autocomplete^3",
    "industry.autocomplete^2",
    "location_name.autocomplete^2",
]


SOURCE_EXCLUDES = [
    "search_text",
]


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    return value or None


def _clean_skills(
    skills: list[str] | None,
) -> list[str]:

    if not skills:
        return []

    result: list[str] = []

    for skill in skills:
        cleaned = _clean_text(skill)

        if cleaned:
            result.append(cleaned.lower())

    return result


def _build_keyword_queries(
    keyword: str,
) -> list[dict]:

    queries: list[dict] = []

    queries.append(
        {
            "multi_match": {
                "query": keyword,
                "fields": FULL_TEXT_FIELDS,
                "type": "best_fields",
                "operator": "and",
                "boost": 2.0,
            }
        }
    )

    queries.append(
        {
            "multi_match": {
                "query": keyword,
                "fields": AUTOCOMPLETE_FIELDS,
                "type": "best_fields",
                "operator": "and",
                "boost": 1.5,
            }
        }
    )

    if len(keyword) >= 4:
        queries.append(
            {
                "multi_match": {
                    "query": keyword,
                    "fields": [
                        "full_name^4",
                        "job_title^4",
                        "skills^4",
                        "job_company_name^2",
                        "industry",
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                    "prefix_length": 1,
                    "boost": 0.5,
                }
            }
        )

    return queries


def _build_search_query(
    keyword: str | None = None,
    skills: list[str] | None = None,
    job_title: str | None = None,
) -> tuple[dict, bool]:

    keyword = _clean_text(keyword)
    job_title = _clean_text(job_title)
    skills = _clean_skills(skills)

    filters: list[dict] = []


    for skill in skills:
        filters.append(
            {
                "match": {
                    "skills.autocomplete": {
                        "query": skill,
                        "operator": "and",
                    }
                }
            }
        )


    if job_title:
        filters.append(
            {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "job_title.autocomplete": {
                                    "query": job_title,
                                    "operator": "and",
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "job_title": {
                                    "query": job_title,
                                }
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            }
        )


    if keyword:

        query = {
            "bool": {
                "should": _build_keyword_queries(
                    keyword
                ),
                "minimum_should_match": 1,
                "filter": filters,
            }
        }

        return query, True


    query = {
        "bool": {
            "must": [
                {
                    "match_all": {},
                }
            ],
            "filter": filters,
        }
    }

    return query, False



def _extract_total(
    total: int | dict | None,
) -> int:

    if isinstance(total, int):
        return total

    if isinstance(total, dict):
        return int(
            total.get("value", 0)
        )

    return 0



async def search_profiles(
    keyword: str | None = None,
    skills: list[str] | None = None,
    job_title: str | None = None,
    page: int = 1,
    page_size: int = 12,
) -> dict:


    page = max(page, 1)

    page_size = max(
        1,
        min(page_size, 100)
    )

    offset = (
        page - 1
    ) * page_size


    query, has_keyword = _build_search_query(
        keyword=keyword,
        skills=skills,
        job_title=job_title,
    )


    if has_keyword:

        sort = [
            {
                "_score": {
                    "order": "desc",
                }
            },
            {
                "full_name.keyword": {
                    "order": "asc",
                    "missing": "_last",
                }
            },
        ]

    else:

        sort = [
            {
                "full_name.keyword": {
                    "order": "asc",
                    "missing": "_last",
                }
            }
        ]


    try:

        response = await es.search(
            index=settings.elasticsearch_index,
            query=query,
            from_=offset,
            size=page_size,
            sort=sort,
            source_excludes=SOURCE_EXCLUDES,
            track_total_hits=True,
        )


    except NotFoundError as exc:

        raise RuntimeError(
            "Elasticsearch profile index does not exist."
        ) from exc


    except (
        ApiError,
        ElasticsearchConnectionError,
    ) as exc:

        print(
            f"Elasticsearch unavailable: {exc}"
        )

        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "pages": 0,
        }


    hits = response.get(
        "hits",
        {}
    )


    total = _extract_total(
        hits.get("total")
    )


    items = [
        hit.get("_source", {})
        for hit in hits.get(
            "hits",
            []
        )
    ]


    pages = (
        ceil(total / page_size)
        if total
        else 0
    )


    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }




async def get_profile_filters() -> dict:

    try:

        response = await es.search(
            index=settings.elasticsearch_index,
            size=0,
            aggs={
                "skills": {
                    "terms": {
                        "field": "skills.keyword",
                        "size": 200,
                        "order": {
                            "_key": "asc",
                        },
                    }
                },
                "job_titles": {
                    "terms": {
                        "field": "job_title.keyword",
                        "size": 200,
                        "order": {
                            "_key": "asc",
                        },
                    }
                },
            },
        )


    except NotFoundError as exc:

        raise RuntimeError(
            "Elasticsearch profile index does not exist."
        ) from exc


    except (
        ApiError,
        ElasticsearchConnectionError,
    ) as exc:

        print(
            f"Elasticsearch unavailable: {exc}"
        )

        return {
            "skills": [],
            "job_titles": [],
        }


    aggregations = response.get(
        "aggregations",
        {}
    )


    skill_buckets = (
        aggregations
        .get("skills", {})
        .get("buckets", [])
    )


    job_title_buckets = (
        aggregations
        .get("job_titles", {})
        .get("buckets", [])
    )


    return {

        "skills": [
            bucket["key"]
            for bucket in skill_buckets
        ],

        "job_titles": [
            bucket["key"]
            for bucket in job_title_buckets
        ],
    }



async def get_filters() -> dict:
    return await get_profile_filters()



async def get_filter_options() -> dict:
    return await get_profile_filters()