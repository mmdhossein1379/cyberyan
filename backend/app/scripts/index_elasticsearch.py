from __future__ import annotations

import asyncio

from elasticsearch.helpers import async_bulk
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.profile import Profile
from app.search.client import es
from app.search.index import PROFILE_INDEX_DEFINITION


def profile_to_document(profile: Profile) -> dict:
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "linkedin_url": profile.linkedin_url,
        "industry": profile.industry,
        "job_title": profile.job_title,
        "job_company_name": profile.job_company_name,
        "location_name": profile.location_name,
        "summary": profile.summary,
        "skills": profile.skills or [],
        "education": profile.education,
        "experience": profile.experience,
        "search_text": profile.search_text,
    }


async def ensure_index_exists() -> None:
    index_name = settings.elasticsearch_index

    exists = await es.indices.exists(
        index=index_name
    )

    if exists:
        print(
            f"Elasticsearch index "
            f"'{index_name}' already exists."
        )
        return

    print(
        f"Creating Elasticsearch index "
        f"'{index_name}'..."
    )

    await es.indices.create(
        index=index_name,
        settings=PROFILE_INDEX_DEFINITION["settings"],
        mappings=PROFILE_INDEX_DEFINITION["mappings"],
    )

    print(
        f"Elasticsearch index "
        f"'{index_name}' created."
    )


async def get_elasticsearch_count() -> int:
    index_name = settings.elasticsearch_index

    exists = await es.indices.exists(
        index=index_name
    )

    if not exists:
        return 0

    response = await es.count(
        index=index_name
    )

    return int(response["count"])


async def load_profiles() -> list[Profile]:
    async with SessionLocal() as db:
        result = await db.scalars(
            select(Profile)
            .order_by(Profile.id.asc())
        )

        return list(result.all())


async def index_profiles() -> None:
    try:
        if not await es.ping():
            raise RuntimeError(
                "Elasticsearch is not reachable."
            )

        profiles = await load_profiles()

        postgres_count = len(profiles)

        print(
            f"Found {postgres_count} profiles "
            f"in PostgreSQL."
        )

        if postgres_count == 0:
            print(
                "No profiles found in PostgreSQL. "
                "Skipping Elasticsearch indexing."
            )
            return

        elasticsearch_count = (
            await get_elasticsearch_count()
        )

        if elasticsearch_count == postgres_count:
            print(
                "Elasticsearch already contains "
                f"{elasticsearch_count} profiles. "
                "Indexing skipped."
            )
            return

        await ensure_index_exists()

        actions = [
            {
                "_op_type": "index",
                "_index": settings.elasticsearch_index,
                "_id": str(profile.id),
                "_source": profile_to_document(profile),
            }
            for profile in profiles
        ]

        print(
            f"Indexing {len(actions)} profiles "
            f"into Elasticsearch..."
        )

        success_count, errors = await async_bulk(
            es,
            actions,
            chunk_size=25,
            max_chunk_bytes=10 * 1024 * 1024,
            refresh=False,
            raise_on_error=False,
        )

        if errors:
            print(
                f"Elasticsearch indexing completed "
                f"with {len(errors)} errors."
            )

            for error in errors[:5]:
                print(error)

            raise RuntimeError(
                "Some Elasticsearch documents "
                "could not be indexed."
            )

        await es.indices.refresh(
            index=settings.elasticsearch_index
        )

        final_count = (
            await get_elasticsearch_count()
        )

        print(
            f"Elasticsearch indexing complete: "
            f"{success_count} operations succeeded."
        )

        print(
            f"Elasticsearch now contains "
            f"{final_count} profiles."
        )

        if final_count != postgres_count:
            raise RuntimeError(
                "PostgreSQL and Elasticsearch "
                "profile counts do not match. "
                f"PostgreSQL={postgres_count}, "
                f"Elasticsearch={final_count}"
            )

    finally:
        await es.close()


if __name__ == "__main__":
    asyncio.run(index_profiles())
