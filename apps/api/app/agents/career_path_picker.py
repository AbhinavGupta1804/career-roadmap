"""
Agent 1: Career Path Picker — deterministic scoring + optional LLM enrichment.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.schemas.agents import CareerPathPickerOutput, CareerTrack, TrackType
from app.schemas.data_models import CareerEntry
from app.schemas.intake import CollegeTier, IntakeForm, SkillRating, TechStream
from app.services import data_registry

# Brief weights
W_SKILL = 0.30
W_INTEREST = 0.25
W_DEMAND = 0.20
W_AI_RESILIENCE = 0.15
W_REALISTIC = 0.10

RATING_LEVEL: dict[str, float] = {
    SkillRating.HEARD_OF.value: 0.25,
    SkillRating.WITH_HELP.value: 0.6,
    SkillRating.SOLO.value: 1.0,
}

COMPETITION_ORDER = {"low": 0, "medium": 1, "high": 2}
DIFFICULTY_ORDER = {"low": 0, "medium": 1, "high": 2}

COMMERCE_STREAMS = {TechStream.COMMERCE.value, TechStream.BBA.value}
BUSINESS_INTEREST_TAGS = {
    "Business Analyst",
    "Finance & Accounting",
    "Digital Marketing",
}

HIRING_COMPANIES = {
    "default": ["Razorpay", "Swiggy", "Zoho", "Freshworks", "PhonePe"],
    "ml": ["Google", "Microsoft", "Flipkart", "Razorpay", "PhonePe"],
    "data": ["Flipkart", "Swiggy", "Razorpay", "Meesho", "CRED"],
    "design": ["Razorpay", "PhonePe", "CRED", "Swiggy", "Freshworks"],
    "dev": ["Zoho", "Freshworks", "Razorpay", "Postman", "Atlassian"],
    "security": ["Paytm", "PhonePe", "Razorpay", "Deloitte", "EY"],
    "cloud": ["Amazon", "Microsoft", "Freshworks", "Razorpay", "PhonePe"],
}

ENRICHMENT_PROMPT = """You are Agent 1 (enrichment only) for Indian tech students.
Three career tracks are ALREADY chosen (Stretch, Realistic, Safe). Do NOT change career_slug or type.
Write compelling why_recommended, honest_warning (nullable), and top_hiring_companies (3-5 Indian tech firms).
Keep avg_starting_salary_band, time_to_job_estimate_months, competition_level unchanged from input.
Output ONLY JSON: {"tracks":[...]} with exactly 3 objects. No markdown."""


@dataclass(frozen=True)
class ScoredCareer:
    career: CareerEntry
    fit_score: float
    skill_match: float
    interest_alignment: float
    market_demand: float
    ai_resilience: float
    realistic_for_profile: float
    is_interest_aligned: bool


def _tier_salary_key(college_tier: CollegeTier) -> str:
    if college_tier == CollegeTier.TIER_1:
        return "tier_1"
    if college_tier == CollegeTier.TIER_2:
        return "tier_2"
    return "tier_3"


def _salary_band_label(career: CareerEntry, intake: IntakeForm) -> str:
    key = _tier_salary_key(intake.profile.college_tier)
    band = career.salary_bands[key]
    return f"₹{band.min_lpa:g}–{band.max_lpa:g} LPA"


def _skill_match(intake: IntakeForm, career: CareerEntry) -> float:
    student = {
        s.name.lower(): RATING_LEVEL[s.rating.value]
        for s in intake.skills_and_goals.skills
    }
    if not career.required_skills:
        return 0.35

    scores: list[float] = []
    for req in career.required_skills:
        key = req.lower()
        level = student.get(key, 0.0)
        if level == 0.0:
            for sk, val in student.items():
                if key in sk or sk in key:
                    level = max(level, val * 0.85)
        scores.append(level)
    return sum(scores) / len(scores)


def _interest_alignment(intake: IntakeForm, career: CareerEntry) -> float:
    ranked = [i.value for i in intake.self_assessment.interest_bias]
    tags = set(career.interest_tags)
    if not ranked:
        return 0.25

    total = 0.0
    for idx, interest in enumerate(ranked):
        weight = 1.0 - idx * 0.15
        if interest in tags:
            total += weight
    return min(1.0, total / max(len(ranked), 1))


def _realistic_for_profile(intake: IntakeForm, career: CareerEntry) -> float:
    cgpa_scores = {
        "<6.5": 0.35,
        "6.5–7.5": 0.55,
        "7.5–8.5": 0.78,
        "8.5+": 0.95,
    }
    tier_scores = {
        "Tier 1 (IIT/NIT/IIIT)": 1.0,
        "Tier 2": 0.78,
        "Tier 3": 0.58,
    }
    timeline_months = {
        "3 months": 3,
        "6 months": 6,
        "12 months": 12,
        "2+ years": 24,
    }

    score = 0.2
    score += cgpa_scores.get(intake.profile.cgpa_band.value, 0.5) * 0.35
    score += tier_scores.get(intake.profile.college_tier.value, 0.6) * 0.25

    avail = timeline_months.get(intake.skills_and_goals.timeline_to_job.value, 12)
    if career.typical_months_to_job <= avail:
        score += 0.15
    else:
        score -= min(0.2, (career.typical_months_to_job - avail) * 0.02)

    if cgpa_scores.get(intake.profile.cgpa_band.value, 0.5) < 0.5:
        score -= DIFFICULTY_ORDER[career.entry_difficulty] * 0.08

    return max(0.0, min(1.0, score))


def _stream_career_boost(intake: IntakeForm, career: CareerEntry) -> float:
    """Nudge commerce/BBA students toward analyst and business-facing roles."""
    if intake.profile.stream.value not in COMMERCE_STREAMS:
        return 0.0
    tags = set(career.interest_tags)
    if tags & BUSINESS_INTEREST_TAGS:
        return 0.08
    return 0.0


def _compute_fit(intake: IntakeForm, career: CareerEntry) -> ScoredCareer:
    skill = _skill_match(intake, career)
    interest = _interest_alignment(intake, career)
    demand = career.market_demand_index
    resilience = career.ai_resilience_index
    realistic = _realistic_for_profile(intake, career)

    fit = (
        skill * W_SKILL
        + interest * W_INTEREST
        + demand * W_DEMAND
        + resilience * W_AI_RESILIENCE
        + realistic * W_REALISTIC
        + _stream_career_boost(intake, career)
    )

    return ScoredCareer(
        career=career,
        fit_score=round(fit, 4),
        skill_match=round(skill, 4),
        interest_alignment=round(interest, 4),
        market_demand=round(demand, 4),
        ai_resilience=round(resilience, 4),
        realistic_for_profile=round(realistic, 4),
        is_interest_aligned=interest >= 0.35,
    )


def _eligible_careers(exclude_slugs: set[str]) -> list[CareerEntry]:
    taxonomy = data_registry.load_career_taxonomy()
    risks = data_registry.load_ai_risk_taxonomy()
    eligible: list[CareerEntry] = []
    for career in taxonomy.careers:
        if career.slug in exclude_slugs:
            continue
        if int(risks.careers[career.slug].tier) >= 4:
            continue
        eligible.append(career)
    return eligible


def build_candidate_pool(
    intake: IntakeForm,
    exclude_slugs: set[str] | None = None,
    pool_size: int = 10,
) -> list[ScoredCareer]:
    exclude = exclude_slugs or set()
    scored = [_compute_fit(intake, c) for c in _eligible_careers(exclude)]

    aligned = sorted(
        [s for s in scored if s.is_interest_aligned],
        key=lambda s: s.fit_score,
        reverse=True,
    )
    lateral = sorted(
        [s for s in scored if not s.is_interest_aligned],
        key=lambda s: s.fit_score + s.skill_match * 0.1,
        reverse=True,
    )

    commitment = intake.self_assessment.commitment_slider
    if commitment >= 4:
        n_align, n_lat = 7, 3
    else:
        n_align, n_lat = 5, 5

    pool: list[ScoredCareer] = []
    seen: set[str] = set()

    for item in aligned:
        if len(pool) >= n_align:
            break
        if item.career.slug not in seen:
            pool.append(item)
            seen.add(item.career.slug)

    for item in lateral:
        if len([p for p in pool if not p.is_interest_aligned]) >= n_lat:
            break
        if item.career.slug not in seen:
            pool.append(item)
            seen.add(item.career.slug)

    if len(pool) < pool_size:
        for item in sorted(scored, key=lambda s: s.fit_score, reverse=True):
            if item.career.slug not in seen:
                pool.append(item)
                seen.add(item.career.slug)
            if len(pool) >= pool_size:
                break

    return pool[:pool_size]


def _stretch_score(s: ScoredCareer, intake: IntakeForm) -> float:
    key = _tier_salary_key(intake.profile.college_tier)
    ceiling = s.career.salary_bands[key].max_lpa
    return (
        s.fit_score
        + DIFFICULTY_ORDER[s.career.entry_difficulty] * 0.12
        + ceiling * 0.02
        + s.ai_resilience * 0.05
    )


def _safe_score(s: ScoredCareer) -> float:
    return (
        s.fit_score
        + (2 - COMPETITION_ORDER[s.career.competition_level]) * 0.1
        + (2 - DIFFICULTY_ORDER[s.career.entry_difficulty]) * 0.12
        - s.career.typical_months_to_job * 0.01
    )


def pick_track_assignments(pool: list[ScoredCareer], intake: IntakeForm) -> list[tuple[ScoredCareer, TrackType]]:
    if len(pool) < 3:
        raise ValueError("Need at least 3 careers in pool")

    stretch_pick = max(pool, key=lambda s: _stretch_score(s, intake))
    used = {stretch_pick.career.slug}

    remaining = [s for s in pool if s.career.slug not in used]
    safe_pick = max(remaining, key=_safe_score)
    used.add(safe_pick.career.slug)

    remaining = [s for s in pool if s.career.slug not in used]
    realistic_pick = max(remaining, key=lambda s: s.fit_score)

    return [
        (stretch_pick, TrackType.STRETCH),
        (realistic_pick, TrackType.REALISTIC),
        (safe_pick, TrackType.SAFE),
    ]


def _companies_for(career: CareerEntry) -> list[str]:
    tags = " ".join(career.interest_tags).lower()
    if "machine learning" in tags or "data science" in tags:
        return HIRING_COMPANIES["ml"]
    if "ui/ux" in tags or "design" in tags:
        return HIRING_COMPANIES["design"]
    if "cyber" in tags:
        return HIRING_COMPANIES["security"]
    if "cloud" in tags or "devops" in tags:
        return HIRING_COMPANIES["cloud"]
    if "web" in tags or "mobile" in tags:
        return HIRING_COMPANIES["dev"]
    if "data" in tags or "analyst" in tags:
        return HIRING_COMPANIES["data"]
    return HIRING_COMPANIES["default"]


def _template_enrich(
    scored: ScoredCareer,
    track_type: TrackType,
    intake: IntakeForm,
) -> CareerTrack:
    career = scored.career
    interests = ", ".join(i.value for i in intake.self_assessment.interest_bias[:2])
    why = (
        f"Fit score {scored.fit_score:.2f} — strong alignment with {interests} "
        f"(interest {scored.interest_alignment:.0%}, skills {scored.skill_match:.0%}, "
        f"demand {scored.market_demand:.0%})."
    )
    warning: str | None = None
    if track_type == TrackType.STRETCH:
        warning = (
            f"Stretch path: {career.entry_difficulty} entry bar. "
            "Plan extra portfolio depth vs campus peers."
        )
    elif track_type == TrackType.SAFE and scored.realistic_for_profile >= 0.7:
        warning = "Safer entry, but cap salary growth if you stop upskilling after first job."

    return CareerTrack(
        name=career.name,
        career_slug=career.slug,
        type=track_type,
        why_recommended=why,
        avg_starting_salary_band=_salary_band_label(career, intake),
        time_to_job_estimate_months=career.typical_months_to_job,
        competition_level=career.competition_level,
        top_hiring_companies=_companies_for(career)[:5],
        honest_warning=warning,
    )


def build_tracks(
    intake: IntakeForm,
    exclude_slugs: set[str] | None = None,
) -> CareerPathPickerOutput:
    """Score, pick Stretch/Realistic/Safe, apply template enrichment (no LLM)."""
    pool = build_candidate_pool(intake, exclude_slugs)
    assignments = pick_track_assignments(pool, intake)
    tracks = [_template_enrich(scored, ttype, intake) for scored, ttype in assignments]
    return CareerPathPickerOutput(tracks=tracks)


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise


def enrich_tracks_with_llm(
    base: CareerPathPickerOutput,
    intake: IntakeForm,
    *,
    api_key: str,
    model: str,
) -> tuple[CareerPathPickerOutput, int, int]:
    """LLM rewrites narrative fields only; slugs and types stay locked."""
    import anthropic

    payload = {
        "intake_summary": {
            "stream": intake.profile.stream.value,
            "year": intake.profile.year_of_study.value,
            "interests": [i.value for i in intake.self_assessment.interest_bias],
            "commitment": intake.self_assessment.commitment_slider,
        },
        "locked_tracks": [t.model_dump(mode="json") for t in base.tracks],
    }

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=ENRICHMENT_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, default=str)}],
    )
    text = "\n".join(b.text for b in response.content if b.type == "text")
    enriched = CareerPathPickerOutput.model_validate(_extract_json(text))

    locked = {t.career_slug: t for t in base.tracks}
    merged: list[CareerTrack] = []
    for et in enriched.tracks:
        base_track = locked.get(et.career_slug)
        if not base_track:
            continue
        merged.append(
            base_track.model_copy(
                update={
                    "why_recommended": et.why_recommended,
                    "honest_warning": et.honest_warning,
                    "top_hiring_companies": et.top_hiring_companies[:8],
                }
            )
        )

    if len(merged) != 3:
        return base, response.usage.input_tokens, response.usage.output_tokens
    return (
        CareerPathPickerOutput(tracks=merged),
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
