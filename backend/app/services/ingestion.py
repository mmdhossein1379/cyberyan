from __future__ import annotations

import ast
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LINKEDIN_URL_INDEX = 4
EXPECTED_COLUMNS = 77
_COORD_RE = re.compile(r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$")


@dataclass(slots=True)
class ParsedProfile:
    full_name: str
    linkedin_url: str
    industry: str | None
    job_title: str | None
    job_company_name: str | None
    location_name: str | None
    summary: str | None
    skills: list[str]
    education: list[dict[str, Any]]
    experience: list[dict[str, Any]]
    search_text: str
    quality: int


def parse_literal(value: str | None, fallback: Any = None) -> Any:
    if not value:
        return fallback
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return fallback


def normalize_skills(value: str | None) -> list[str]:
    raw = parse_literal(value, [])
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        return []
    return sorted({item.strip().lower() for item in raw if item.strip()})


def _looks_like_profile(row: list[str]) -> bool:
    return len(row) > LINKEDIN_URL_INDEX and row[LINKEDIN_URL_INDEX].startswith("linkedin.com/in/")


def _normalize_prefix(row: list[str]) -> list[str] | None:
    """Remove a known injected source-path prefix while preserving the actual row."""
    if _looks_like_profile(row):
        return row

    if len(row) > LINKEDIN_URL_INDEX + 1 and row[0].startswith(("H:\\", "C:\\")):
        shifted = row[1:]
        if _looks_like_profile(shifted):
            return shifted

    return None


def _find_experience(row: list[str]) -> tuple[int | None, list[dict[str, Any]]]:
    best_index: int | None = None
    best_items: list[dict[str, Any]] = []
    best_score = -1

    for index, cell in enumerate(row):
        if not cell.lstrip().startswith("["):
            continue
        parsed = parse_literal(cell)
        if not isinstance(parsed, list):
            continue

        items = [item for item in parsed if isinstance(item, dict)]
        score = sum("title" in item and ("company" in item or "organization" in item) for item in items)
        if score > best_score and score > 0:
            best_index = index
            best_items = items
            best_score = score

    return best_index, best_items


def _find_education(row: list[str]) -> list[dict[str, Any]]:
    best_items: list[dict[str, Any]] = []
    for cell in row:
        if not cell.lstrip().startswith("["):
            continue
        parsed = parse_literal(cell)
        if not isinstance(parsed, list):
            continue
        items = [item for item in parsed if isinstance(item, dict) and "school" in item]
        if len(items) > len(best_items):
            best_items = items
    return best_items


def _sanitize_experience(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    safe: list[dict[str, Any]] = []
    for item in items:
        title = item.get("title") if isinstance(item.get("title"), dict) else {}
        company = item.get("company") if isinstance(item.get("company"), dict) else {}
        company_name = company.get("name") if isinstance(company, dict) else None
        title_name = title.get("name") if isinstance(title, dict) else None
        if not title_name and not company_name:
            continue
        safe.append(
            {
                "company": {"name": company_name} if company_name else None,
                "title": {"name": title_name} if title_name else None,
                "start_date": item.get("start_date"),
                "end_date": item.get("end_date"),
                "is_primary": bool(item.get("is_primary")),
            }
        )
    return safe


def _sanitize_education(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    safe: list[dict[str, Any]] = []
    for item in items:
        school = item.get("school") if isinstance(item.get("school"), dict) else {}
        school_name = school.get("name") if isinstance(school, dict) else None
        if not school_name:
            continue
        safe.append(
            {
                "school": {"name": school_name},
                "degrees": item.get("degrees") if isinstance(item.get("degrees"), list) else [],
                "majors": item.get("majors") if isinstance(item.get("majors"), list) else [],
                "start_date": item.get("start_date"),
                "end_date": item.get("end_date"),
            }
        )
    return safe


def _current_experience(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        if item.get("is_primary") is True:
            return item
    for item in items:
        if item.get("end_date") in (None, "") and item.get("title"):
            return item
    return items[0]


def _skills_from_row(row: list[str], experience_index: int | None) -> list[str]:
    # In the source schema skills are five cells before experience. That relative
    # position survives the variable shifts present in malformed records.
    if experience_index is not None and experience_index >= 5:
        skills = normalize_skills(row[experience_index - 5])
        if skills:
            return skills

    # Fallback: choose the most skill-like string list while rejecting contact
    # lists and geographic history lists.
    best_score = -10_000
    best: list[str] = []
    for cell in row:
        values = normalize_skills(cell)
        if not values:
            continue
        if any("@" in value or value.startswith("+") for value in values):
            continue
        location_like = sum("united states" in value or value.count(",") >= 2 for value in values)
        score = len(values) - (3 * location_like)
        if score > best_score:
            best_score = score
            best = values
    return best


def _summary_from_row(row: list[str], experience_index: int | None) -> str | None:
    if experience_index is None or experience_index < 9:
        return None
    value = row[experience_index - 9].strip()
    if not value or value.startswith(("[", "{")):
        return None
    return value


def _location_from_row(row: list[str], cutoff: int) -> str | None:
    candidates: list[str] = []
    for index, cell in enumerate(row[:cutoff]):
        value = cell.strip()
        if value.count(",") < 2:
            continue
        next_cells = row[index + 1 : min(cutoff, index + 10)]
        if any(_COORD_RE.match(candidate.strip()) for candidate in next_cells):
            candidates.append(value)
    return candidates[-1] if candidates else None


def _field_from_current_experience(
    experience: dict[str, Any] | None,
    parent: str,
    field: str,
) -> str | None:
    if not experience:
        return None
    value = experience.get(parent)
    if isinstance(value, dict):
        result = value.get(field)
        return str(result).strip() if result else None
    return None


def _company_industry(experience: dict[str, Any] | None) -> str | None:
    if not experience:
        return None
    company = experience.get("company")
    if isinstance(company, dict):
        value = company.get("industry")
        return str(value).strip() if value else None
    return None


def _build_search_text(profile: ParsedProfile) -> str:
    experience_text = " ".join(
        filter(
            None,
            [
                _field_from_current_experience(item, "title", "name")
                for item in profile.experience
            ]
            + [
                _field_from_current_experience(item, "company", "name")
                for item in profile.experience
            ],
        )
    )
    education_text = " ".join(
        filter(
            None,
            [
                _field_from_current_experience(item, "school", "name")
                for item in profile.education
            ],
        )
    )
    fields = [
        profile.full_name,
        profile.industry or "",
        profile.job_title or "",
        profile.job_company_name or "",
        profile.location_name or "",
        profile.summary or "",
        " ".join(profile.skills),
        experience_text,
        education_text,
    ]
    return " ".join(value.strip() for value in fields if value and value.strip())


def _parse_profile(row: list[str]) -> ParsedProfile:
    experience_index, raw_experience = _find_experience(row)
    raw_education = _find_education(row)
    current = _current_experience(raw_experience)

    job_title = _field_from_current_experience(current, "title", "name")
    company_name = _field_from_current_experience(current, "company", "name")
    industry = _company_industry(current)
    skills = _skills_from_row(row, experience_index)
    summary = _summary_from_row(row, experience_index)
    cutoff = max(0, (experience_index - 9) if experience_index is not None else len(row))
    location = _location_from_row(row, cutoff)

    safe_experience = _sanitize_experience(raw_experience)
    safe_education = _sanitize_education(raw_education)
    quality = (
        4 * bool(job_title)
        + 3 * bool(company_name)
        + 2 * bool(skills)
        + bool(location)
        + bool(summary)
    )

    profile = ParsedProfile(
        full_name=row[0].strip() or "Unknown",
        linkedin_url=row[LINKEDIN_URL_INDEX].strip(),
        industry=industry,
        job_title=job_title,
        job_company_name=company_name,
        location_name=location,
        summary=summary,
        skills=skills,
        education=safe_education,
        experience=safe_experience,
        search_text="",
        quality=quality,
    )
    profile.search_text = _build_search_text(profile)
    return profile


def parse_dataset(path: Path) -> tuple[list[ParsedProfile], dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if len(header) != EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected dataset schema: {len(header)} columns")

        by_linkedin_url: dict[str, ParsedProfile] = {}
        raw_records = 0
        skipped_records = 0

        for raw_row in reader:
            raw_records += 1
            row = _normalize_prefix(raw_row)
            if row is None:
                skipped_records += 1
                continue

            profile = _parse_profile(row)
            previous = by_linkedin_url.get(profile.linkedin_url)
            if previous is None or profile.quality > previous.quality:
                by_linkedin_url[profile.linkedin_url] = profile

    profiles = sorted(by_linkedin_url.values(), key=lambda item: item.full_name.lower())
    stats = {
        "raw_records": raw_records,
        "usable_unique_profiles": len(profiles),
        "skipped_records": skipped_records,
        "profiles_with_job_title": sum(bool(item.job_title) for item in profiles),
        "profiles_with_skills": sum(bool(item.skills) for item in profiles),
        "profiles_with_location": sum(bool(item.location_name) for item in profiles),
    }
    return profiles, stats
