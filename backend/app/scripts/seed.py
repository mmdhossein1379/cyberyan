import asyncio
from pathlib import Path

from sqlalchemy import select, func

from app.db.session import SessionLocal
from app.models.profile import Profile
from app.core.config import settings
from app.services.ingestion import parse_dataset


async def seed():

    async with SessionLocal() as session:

        result = await session.execute(
            select(func.count(Profile.id))
        )

        count = result.scalar_one()

        if count > 0:
            print(
                f"Seed skipped: profiles table already contains {count} rows."
            )
            return


        print("Loading dataset...")

        profiles, stats = parse_dataset(
            Path(settings.dataset_path)
        )

        print(
            f"Parsed {stats['usable_unique_profiles']} profiles."
        )


        objects = []

        for item in profiles:
            objects.append(
                Profile(
                    full_name=item.full_name,
                    linkedin_url=item.linkedin_url,
                    industry=item.industry,
                    job_title=item.job_title,
                    job_company_name=item.job_company_name,
                    location_name=item.location_name,
                    summary=item.summary,
                    skills=item.skills,
                    education=item.education,
                    experience=item.experience,
                    search_text=item.search_text,
                )
            )


        session.add_all(objects)

        await session.commit()


        print(
            f"Seed completed: {len(objects)} profiles inserted."
        )


if __name__ == "__main__":
    asyncio.run(seed())