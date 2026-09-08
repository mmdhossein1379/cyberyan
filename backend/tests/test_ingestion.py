from pathlib import Path

from app.services.ingestion import normalize_skills, parse_dataset


def test_normalize_skills_deduplicates_and_lowercases() -> None:
    assert normalize_skills("['Python', 'python', ' SQL ']") == ["python", "sql"]


def test_supplied_dataset_is_cleaned_and_deduplicated() -> None:
    dataset = Path(__file__).parents[2] / "data" / "300 user linkedin.txt"
    if not dataset.exists():
        return

    profiles, stats = parse_dataset(dataset)
    assert len({profile.linkedin_url for profile in profiles}) == len(profiles)
    assert stats["usable_unique_profiles"] >= 250
    assert stats["profiles_with_job_title"] >= 250

    abelardo = next(profile for profile in profiles if "abelardo-pequeno" in profile.linkedin_url)
    assert abelardo.job_title == "territory manager"
    assert abelardo.job_company_name == "u.s. & texas lawshield®"
    assert "time management" in abelardo.skills
