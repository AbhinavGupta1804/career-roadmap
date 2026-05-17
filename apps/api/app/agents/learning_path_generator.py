"""
Agent 4: Learning Path Generator — ordered gaps, timeline, budget-filtered resources.

Timeline (from brief):
  1hr/day → ~6 months (26 weeks)
  2–3hr/day → ~3–4 months (12 weeks)
  4+hr/day → ~2 months (8 weeks)
"""

from __future__ import annotations

import math
from typing import Any

from app.agents.skill_gap_analyzer import (
    _canonical_display,
    _normalize_skill_key,
    analyze_skill_gaps,
)
from app.schemas.agents import (
    LearningPathGeneratorOutput,
    LearningWeek,
    SkillGapAnalyzerOutput,
    SkillGapItem,
)
from app.schemas.data_models import LearningResource
from app.schemas.intake import BudgetInr, HoursPerDay, IntakeForm
from app.services import data_registry

# Target plan length by daily study time
TIMELINE_WEEKS: dict[HoursPerDay, int] = {
    HoursPerDay.ONE: 26,
    HoursPerDay.TWO_TO_THREE: 12,
    HoursPerDay.FOUR_PLUS: 8,
}

WEEKLY_HOURS: dict[HoursPerDay, int] = {
    HoursPerDay.ONE: 7,
    HoursPerDay.TWO_TO_THREE: 10,
    HoursPerDay.FOUR_PLUS: 14,
}

PRIORITY_RANK = {"must": 0, "should": 1, "nice": 2}

# Prerequisites (normalized keys) — foundational skills scheduled first
PREREQUISITES: dict[str, list[str]] = {
    "excel": [],
    "python": [],
    "javascript": [],
    "sql": ["excel"],
    "statistics": ["python"],
    "power bi": ["sql", "excel"],
    "tableau": ["sql"],
    "postgresql": ["sql"],
    "django": ["python"],
    "flask": ["python"],
    "fastapi": ["python"],
    "react": ["javascript"],
    "docker": ["python"],
    "kubernetes": ["docker"],
    "redis": ["python"],
    "aws": ["python"],
    "rest": ["python"],
    "machine learning": ["python", "statistics"],
    "ml basics": ["python"],
}


def total_weeks_for_student(hours_per_day: HoursPerDay) -> int:
    return TIMELINE_WEEKS[hours_per_day]


def order_gaps_by_dependency(gaps: list[SkillGapItem]) -> list[SkillGapItem]:
    """Topological order with must-have / high-demand skills breaking ties."""
    by_key = {_normalize_skill_key(g.name): g for g in gaps}
    ordered_keys: list[str] = []
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(key: str) -> None:
        if key in visited or key not in by_key:
            return
        if key in visiting:
            return
        visiting.add(key)
        for dep in PREREQUISITES.get(key, []):
            visit(dep)
        visiting.discard(key)
        visited.add(key)
        ordered_keys.append(key)

    sorted_gaps = sorted(
        gaps,
        key=lambda g: (
            PRIORITY_RANK[g.priority],
            -g.demand_frequency_pct,
            -g.weeks_to_bridge,
        ),
    )
    for gap in sorted_gaps:
        visit(_normalize_skill_key(gap.name))

    return [by_key[k] for k in ordered_keys]


def _budget_allows(resource: LearningResource, budget: BudgetInr) -> bool:
    if budget in (BudgetInr.ZERO, BudgetInr.LOW):
        return resource.cost == "free" and resource.cost_inr_max <= 2_000
    if budget == BudgetInr.MID:
        return resource.cost_inr_max <= 10_000
    return True


def _resource_matches_skill(resource: LearningResource, skill_key: str) -> bool:
    for taught in resource.skills_taught:
        tk = _normalize_skill_key(taught)
        if tk == skill_key or skill_key in tk or tk in skill_key:
            return True
    return False


def pick_resources_for_skill(
    skill_name: str,
    library: list[LearningResource],
    budget: BudgetInr,
    *,
    limit: int = 3,
) -> list[str]:
    skill_key = _normalize_skill_key(skill_name)
    eligible = [r for r in library if _budget_allows(r, budget)]
    matches: list[LearningResource] = []
    for resource in eligible:
        if _resource_matches_skill(resource, skill_key):
            matches.append(resource)

    matches.sort(key=lambda r: (0 if r.cost == "free" else 1, r.cost_inr_max, r.hours))
    if matches:
        return [f"{r.title} ({r.provider or r.type})" for r in matches[:limit]]

    # Visualization-adjacent fallback for BI tools
    if skill_key in ("tableau", "power bi"):
        for resource in eligible:
            if any(
                _normalize_skill_key(t) in ("visualization", "power bi", "tableau")
                for t in resource.skills_taught
            ):
                return [f"{resource.title} ({resource.provider or resource.type})"]

    return [
        f"{_canonical_display(skill_name)} — official docs + one hands-on exercise (free)",
    ]


def _compress_durations(
    blocks: list[tuple[SkillGapItem, int]],
    total_weeks: int,
) -> list[tuple[SkillGapItem, int]]:
    if not blocks:
        return []
    used = sum(w for _, w in blocks)
    if used <= total_weeks:
        return blocks

    ratio = total_weeks / used
    compressed: list[tuple[SkillGapItem, int]] = []
    for gap, weeks in blocks:
        floor = 1 if gap.priority == "must" else 1
        compressed.append((gap, max(floor, int(math.floor(weeks * ratio)))))
    while sum(w for _, w in compressed) > total_weeks:
        idx = max(
            range(len(compressed)),
            key=lambda i: compressed[i][1]
            if compressed[i][0].priority != "must"
            else -1,
        )
        gap, weeks = compressed[idx]
        if weeks > 1:
            compressed[idx] = (gap, weeks - 1)
        else:
            break
    return compressed


def _build_skill_blocks(
    ordered_gaps: list[SkillGapItem],
    total_weeks: int,
) -> list[tuple[SkillGapItem, int]]:
    blocks: list[tuple[SkillGapItem, int]] = []
    for gap in ordered_gaps:
        weeks = gap.weeks_to_bridge
        if weeks <= 0 and gap.required_level > gap.current_level:
            weeks = 1
        if weeks > 0:
            blocks.append((gap, weeks))
    return _compress_durations(blocks, total_weeks)


def _mini_task_for_week(gap: SkillGapItem, week_in_skill: int, total_in_skill: int) -> str:
    skill = gap.name
    if week_in_skill == 1:
        return (
            f"Complete the intro module for {skill} and write 5 bullet notes "
            f"on what employers expect (JD-aligned)."
        )
    if week_in_skill == total_in_skill:
        return (
            f"Ship a small {skill} deliverable (notebook, dashboard slice, or script) "
            f"and add it to your portfolio README."
        )
    return (
        f"Practice {skill}: finish one exercise set and one mock interview question "
        f"out loud."
    )


def build_learning_weeks(
    ordered_gaps: list[SkillGapItem],
    total_weeks: int,
    hours_per_day: HoursPerDay,
    library: list[LearningResource],
    budget: BudgetInr,
) -> list[LearningWeek]:
    hours_per_week = WEEKLY_HOURS[hours_per_day]
    blocks = _build_skill_blocks(ordered_gaps, total_weeks)
    weeks: list[LearningWeek] = []
    week_num = 0

    for gap, duration in blocks:
        resources = pick_resources_for_skill(gap.name, library, budget)
        for part in range(1, duration + 1):
            if week_num >= total_weeks:
                break
            week_num += 1
            weeks.append(
                LearningWeek(
                    week=week_num,
                    focus_skill=gap.name,
                    resources=resources,
                    hours=hours_per_week,
                    mini_task=_mini_task_for_week(gap, part, duration),
                    checkpoint=week_num % 4 == 0,
                )
            )
        if week_num >= total_weeks:
            break

    filler_focus = "Portfolio & interview prep"
    filler_resources = pick_resources_for_skill("SQL", library, budget)[:1] or [
        "GitHub portfolio README template (free)",
    ]
    while week_num < total_weeks:
        week_num += 1
        weeks.append(
            LearningWeek(
                week=week_num,
                focus_skill=filler_focus,
                resources=filler_resources,
                hours=hours_per_week,
                mini_task=(
                    "Polish one portfolio project, update LinkedIn, and do one "
                    "mock HR + one technical screen."
                ),
                checkpoint=week_num % 4 == 0 or week_num == total_weeks,
            )
        )

    if weeks:
        weeks[-1] = weeks[-1].model_copy(update={"checkpoint": True})

    return weeks


def generate_learning_path(
    intake: IntakeForm,
    career_slug: str,
    *,
    skill_gap: SkillGapAnalyzerOutput | None = None,
    resources: list[LearningResource] | None = None,
    role_name: str | None = None,
) -> LearningPathGeneratorOutput:
    if skill_gap is None:
        skill_gap = analyze_skill_gaps(
            intake,
            career_slug,
            role_name or career_slug.replace("-", " ").title(),
        )

    library = resources or data_registry.load_resource_library().resources
    total_weeks = total_weeks_for_student(intake.profile.hours_per_day)
    ordered = order_gaps_by_dependency(skill_gap.skills)
    weeks = build_learning_weeks(
        ordered,
        total_weeks,
        intake.profile.hours_per_day,
        library,
        intake.profile.budget_inr,
    )

    return LearningPathGeneratorOutput(total_weeks=len(weeks), weeks=weeks)


def parse_skill_gap_from_input(agent_input: dict[str, Any]) -> SkillGapAnalyzerOutput | None:
    raw = agent_input.get("skill_gap")
    if not raw:
        return None
    return SkillGapAnalyzerOutput.model_validate(raw)
