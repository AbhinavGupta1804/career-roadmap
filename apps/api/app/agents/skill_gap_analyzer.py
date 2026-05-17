"""
Agent 3: Skill Gap Analyzer — JD corpus frequency + student self-ratings.

Pipeline:
1. Load cached JDs for the chosen role
2. (Live) Haiku extraction pass normalizes skills per JD; (mock) use skills_mentioned
3. Build skill frequency map; keep skills appearing in >= 15% of JDs
4. Compare to student self-ratings → gap matrix with weeks_to_bridge
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Literal

from app.schemas.agents import SkillGapAnalyzerOutput, SkillGapItem
from app.schemas.data_models import RoleJdCache
from app.schemas.intake import HoursPerDay, IntakeForm, SkillRating
from app.services import data_registry

JD_FREQUENCY_THRESHOLD_PCT = 15.0
MAX_GAP_SKILLS = 14

EXTRACTION_PROMPT = """You extract technical skills from Indian tech fresher job descriptions.

For EACH job description below, list skills explicitly required or strongly implied.
Use short canonical names (e.g. "SQL", "Python", "Power BI", "REST APIs", "Docker").

Output ONLY valid JSON (no markdown):
{"jds":[{"id":"<exact jd id>","skills":["Skill1","Skill2"]}]}

Rules:
- Include only technical/tool/domain skills (not soft skills like "communication")
- Max 12 skills per JD
- Prefer names from the provided skills_mentioned hints when present
"""

RATING_TO_LEVEL: dict[SkillRating, int] = {
    SkillRating.HEARD_OF: 1,
    SkillRating.WITH_HELP: 2,
    SkillRating.SOLO: 4,
}

# Aliases for fuzzy student ↔ JD skill matching
_SKILL_ALIASES: dict[str, str] = {
    "powerbi": "power bi",
    "power-bi": "power bi",
    "ms excel": "excel",
    "microsoft excel": "excel",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "py": "python",
    "js": "javascript",
    "node": "nodejs",
    "node.js": "nodejs",
    "ml": "machine learning",
    "ai": "machine learning",
}


def _normalize_skill_key(name: str) -> str:
    key = name.strip().lower()
    key = re.sub(r"\s+", " ", key)
    return _SKILL_ALIASES.get(key, key)


_CANONICAL_DISPLAY: dict[str, str] = {
    "sql": "SQL",
    "python": "Python",
    "excel": "Excel",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "statistics": "Statistics",
    "postgresql": "PostgreSQL",
    "redis": "Redis",
    "django": "Django",
    "rest": "REST",
    "aws": "AWS",
    "javascript": "JavaScript",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "machine learning": "Machine Learning",
}


def _canonical_display(name: str) -> str:
    stripped = name.strip()
    if not stripped:
        return stripped
    key = _normalize_skill_key(stripped)
    if key in _CANONICAL_DISPLAY:
        return _CANONICAL_DISPLAY[key]
    return stripped.title()


def skills_per_jd_from_cache(cache: RoleJdCache) -> list[list[str]]:
    """Deterministic skills per JD from cached skills_mentioned."""
    return [
        [_canonical_display(s) for s in jd.skills_mentioned if s.strip()]
        for jd in cache.jds
    ]


def build_skill_frequency_map(
    skills_per_jd: list[list[str]],
    *,
    jd_count: int | None = None,
) -> dict[str, float]:
    """
    Map canonical skill display name → % of JDs mentioning it (unique per JD).
    """
    total = jd_count if jd_count is not None else len(skills_per_jd)
    if total <= 0:
        return {}

    counts: Counter[str] = Counter()
    display_by_key: dict[str, str] = {}

    for jd_skills in skills_per_jd:
        seen_keys: set[str] = set()
        for raw in jd_skills:
            key = _normalize_skill_key(raw)
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)
            display_by_key.setdefault(key, _canonical_display(raw))
            counts[display_by_key[key]] += 1

    return {
        skill: round(100.0 * count / total, 1)
        for skill, count in counts.items()
    }


def filter_skills_by_threshold(
    frequency_map: dict[str, float],
    threshold_pct: float = JD_FREQUENCY_THRESHOLD_PCT,
) -> list[tuple[str, float]]:
    """Skills appearing in at least threshold_pct of JDs, highest frequency first."""
    kept = [(name, pct) for name, pct in frequency_map.items() if pct >= threshold_pct]
    kept.sort(key=lambda x: (-x[1], x[0]))
    return kept[:MAX_GAP_SKILLS]


def _student_skill_levels(intake: IntakeForm) -> dict[str, int]:
    levels: dict[str, int] = {}
    for skill in intake.skills_and_goals.skills:
        levels[_normalize_skill_key(skill.name)] = RATING_TO_LEVEL[skill.rating]
    return levels


def _student_level_for_jd_skill(skill_name: str, student_levels: dict[str, int]) -> int:
    key = _normalize_skill_key(skill_name)
    if key in student_levels:
        return student_levels[key]

    # Substring / token overlap (e.g. "REST APIs" ↔ student "REST")
    for student_key, level in student_levels.items():
        if student_key in key or key in student_key:
            return level
    return 0


def required_level_for_frequency(freq_pct: float) -> int:
    if freq_pct >= 80:
        return 4
    if freq_pct >= 50:
        return 3
    if freq_pct >= 25:
        return 2
    return 2


def weeks_to_bridge(
    current_level: int,
    required_level: int,
    hours_per_day: HoursPerDay,
) -> int:
    gap = max(0, required_level - current_level)
    if gap == 0:
        return 0
    pace = {
        HoursPerDay.ONE: 1.4,
        HoursPerDay.TWO_TO_THREE: 1.0,
        HoursPerDay.FOUR_PLUS: 0.75,
    }[hours_per_day]
    return max(1, min(52, int(math.ceil(gap * 3 * pace))))


def _priority_for(
    freq_pct: float,
    gap: int,
    rank: int,
) -> Literal["must", "should", "nice"]:
    if rank < 3 and freq_pct >= 50 and gap >= 2:
        return "must"
    if rank < 5 and (freq_pct >= 30 or gap >= 1):
        return "should"
    return "nice"


def build_gap_items(
    intake: IntakeForm,
    role_skills: list[tuple[str, float]],
) -> list[SkillGapItem]:
    student_levels = _student_skill_levels(intake)
    hours = intake.profile.hours_per_day
    items: list[SkillGapItem] = []

    for rank, (skill_name, freq_pct) in enumerate(role_skills):
        current = _student_level_for_jd_skill(skill_name, student_levels)
        required = required_level_for_frequency(freq_pct)
        gap = max(0, required - current)
        items.append(
            SkillGapItem(
                name=skill_name,
                current_level=current,
                required_level=required,
                demand_frequency_pct=freq_pct,
                weeks_to_bridge=weeks_to_bridge(current, required, hours),
                priority=_priority_for(freq_pct, gap, rank),
            )
        )
    return items


def analyze_skill_gaps(
    intake: IntakeForm,
    career_slug: str,
    role_name: str,
    *,
    skills_per_jd: list[list[str]] | None = None,
) -> SkillGapAnalyzerOutput:
    """
    Full Agent 3 pipeline from JD skill lists (cached or Haiku-extracted).
    """
    if skills_per_jd is None:
        try:
            cache = data_registry.load_jd_cache(career_slug)
            skills_per_jd = skills_per_jd_from_cache(cache)
            jd_count = len(cache.jds)
        except FileNotFoundError:
            career = next(
                c
                for c in data_registry.load_career_taxonomy().careers
                if c.slug == career_slug
            )
            skills_per_jd = [[s] for s in career.required_skills]
            jd_count = len(skills_per_jd)
    else:
        jd_count = len(skills_per_jd)

    frequency_map = build_skill_frequency_map(skills_per_jd, jd_count=jd_count)
    role_skills = filter_skills_by_threshold(frequency_map)

    if not role_skills:
        career = next(
            (
                c
                for c in data_registry.load_career_taxonomy().careers
                if c.slug == career_slug
            ),
            None,
        )
        if career:
            role_skills = [(s, 100.0) for s in career.required_skills[:6]]

    items = build_gap_items(intake, role_skills)
    return SkillGapAnalyzerOutput(
        role=role_name,
        career_slug=career_slug,
        skills=items,
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise


def extract_skills_with_haiku(
    cache: RoleJdCache,
    *,
    api_key: str,
    model: str,
) -> tuple[list[list[str]], int, int]:
    """
    Haiku pass: extract/normalize skills per JD from descriptions.
    Falls back to skills_mentioned for any JD missing from the response.
    """
    import anthropic

    payload = {
        "role": cache.role_name,
        "jds": [
            {
                "id": jd.id,
                "title": jd.title,
                "company": jd.company,
                "description": jd.description,
                "skills_mentioned_hints": jd.skills_mentioned,
            }
            for jd in cache.jds
        ],
    }

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=EXTRACTION_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, default=str)}],
    )
    text = "\n".join(b.text for b in response.content if b.type == "text")
    parsed = _extract_json(text)

    by_id: dict[str, list[str]] = {}
    for entry in parsed.get("jds", []):
        jd_id = entry.get("id")
        skills = entry.get("skills") or []
        if jd_id and isinstance(skills, list):
            by_id[jd_id] = [
                _canonical_display(str(s)) for s in skills if str(s).strip()
            ]

    fallback = skills_per_jd_from_cache(cache)
    merged: list[list[str]] = []
    for idx, jd in enumerate(cache.jds):
        extracted = by_id.get(jd.id, [])
        cached = fallback[idx]
        # Union per JD (dedupe by normalized key)
        keys_seen: set[str] = set()
        combined: list[str] = []
        for skill in extracted + cached:
            key = _normalize_skill_key(skill)
            if key and key not in keys_seen:
                keys_seen.add(key)
                combined.append(_canonical_display(skill))
        merged.append(combined)

    return (
        merged,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
