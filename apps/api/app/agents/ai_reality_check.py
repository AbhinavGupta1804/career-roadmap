"""
Agent 2: AI Reality Check — tier tagging from taxonomy + disruption briefing + optional LLM polish.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.schemas.agents import (
    AiRealityCheckOutput,
    AiRiskTier,
    CareerPathPickerOutput,
    CareerTrack,
    DisruptionBriefing,
)
from app.schemas.data_models import CareerEntry
from app.schemas.intake import IntakeForm
from app.services import data_registry

TIER_HEAVY_OR_SUNSET = {AiRiskTier.HEAVY.value, AiRiskTier.SUNSET.value}

ENRICHMENT_PROMPT = """You are Agent 2 (enrichment only) for Indian tech careers.
Tier numbers (ai_risk_tier) and career_slug are LOCKED — do not change them.
You may refine: replaces[], amplifies[], evolved_role_2029, survival_skills[] per track,
and the full disruption_briefing (summary, rejected_paths, do_not_pursue_callouts).
Be honest about AI disruption for Indian freshers in 2026. Output ONLY valid JSON matching
AiRealityCheckOutput schema. No markdown."""


def _tier_for_slug(slug: str) -> tuple[AiRiskTier, str]:
    risks = data_registry.load_ai_risk_taxonomy()
    profile = risks.careers[slug]
    tier_num = int(profile.tier)
    tier = AiRiskTier(tier_num)
    label = risks.tier_definitions[str(tier_num)].label
    return tier, label


def _profile_for_slug(slug: str):
    return data_registry.load_ai_risk_taxonomy().careers[slug]


def patch_track(track: CareerTrack) -> CareerTrack:
    """Apply tier + taxonomy fields to one Agent 1 track."""
    tier, label = _tier_for_slug(track.career_slug)
    profile = _profile_for_slug(track.career_slug)
    return track.model_copy(
        update={
            "ai_risk_tier": tier,
            "ai_risk_label": label,
            "replaces": list(profile.replaces),
            "amplifies": list(profile.amplifies),
            "evolved_role_2029": profile.evolved_role_2029,
            "survival_skills": list(profile.survival_skills),
        }
    )


def tracks_requiring_repick(tracks: list[CareerTrack]) -> list[CareerTrack]:
    """Tier 4 or 5 — must not ship as primary recommendations."""
    return [
        t
        for t in tracks
        if t.ai_risk_tier is not None and t.ai_risk_tier.value in TIER_HEAVY_OR_SUNSET
    ]


def assert_plan_safe(output: AiRealityCheckOutput) -> None:
    bad = tracks_requiring_repick(output.tracks)
    if bad:
        names = ", ".join(t.name for t in bad)
        raise ValueError(f"Plan contains tier 4/5 primary tracks: {names}")


def _interest_set(intake: IntakeForm) -> set[str]:
    return {i.value for i in intake.self_assessment.interest_bias}


def _do_not_pursue_callouts(intake: IntakeForm) -> list[str]:
    """Call out high-risk careers that match stated interests but were not recommended."""
    interests = _interest_set(intake)
    risks = data_registry.load_ai_risk_taxonomy()
    taxonomy = data_registry.load_career_taxonomy()
    callouts: list[str] = []

    for career in taxonomy.careers:
        tier_num = int(risks.careers[career.slug].tier)
        if tier_num < 4:
            continue
        if not (set(career.interest_tags) & interests):
            continue
        label = risks.tier_definitions[str(tier_num)].label
        alt = _suggest_alternative(career, taxonomy, risks)
        callouts.append(
            f"We did NOT suggest {career.name} as a primary path — "
            f"AI Risk Tier {tier_num} ({label}). {alt}"
        )

    if not callouts:
        callouts.append(
            "We filtered out tier 4–5 sunset paths from your candidate set "
            "(e.g. generic content mills, entry-level roles heavily automated by 2028)."
        )
    return callouts[:4]


def _suggest_alternative(
    risky: CareerEntry,
    taxonomy: list[CareerEntry] | Any,
    risks: Any,
) -> str:
    """Short routing hint toward a safer adjacent role."""
    careers = taxonomy.careers if hasattr(taxonomy, "careers") else taxonomy
    tags = set(risky.interest_tags)
    for c in careers:
        if c.slug == risky.slug:
            continue
        if int(risks.careers[c.slug].tier) >= 4:
            continue
        if set(c.interest_tags) & tags:
            return f"Consider {c.name} instead — similar interest signal, safer disruption tier."
    return "Explore the three recommended tracks below — they honor your interests on the safer side of disruption."


def _build_disruption_briefing(
    patched_tracks: list[CareerTrack],
    intake: IntakeForm,
    rejected_paths: list[str] | None = None,
) -> DisruptionBriefing:
    tiers = [t.ai_risk_tier.value for t in patched_tracks if t.ai_risk_tier]
    tier_summary = ", ".join(
        f"{t.name} (Tier {t.ai_risk_tier.value})" for t in patched_tracks if t.ai_risk_tier
    )

    summary = (
        f"Your three primary paths sit at disruption tiers: {tier_summary}. "
        "None are tier 4–5 sunset roles. In 2026–2029, success depends on skills AI cannot "
        "replicate: judgment, domain context, and shipping real outcomes — not tool clicking."
    )

    if any(t.ai_risk_tier == AiRiskTier.PARTIAL for t in patched_tracks):
        summary += (
            " At least one path has entry-level automation pressure — "
            "prioritize portfolio depth and communication early."
        )

    return DisruptionBriefing(
        summary=summary,
        rejected_paths=rejected_paths or [],
        do_not_pursue_callouts=_do_not_pursue_callouts(intake),
    )


def apply_reality_check(
    picker_output: CareerPathPickerOutput,
    intake: IntakeForm,
    *,
    rejected_paths: list[str] | None = None,
) -> AiRealityCheckOutput:
    """
    Patch Agent 1 tracks with taxonomy tiers and emit disruption briefing.
    Does not guarantee tier safety — orchestrator must re-pick if any track is tier 4/5.
    """
    patched = [patch_track(t) for t in picker_output.tracks]
    briefing = _build_disruption_briefing(patched, intake, rejected_paths)
    return AiRealityCheckOutput(tracks=patched, disruption_briefing=briefing)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise


def _merge_llm_enrichment(
    base: AiRealityCheckOutput,
    enriched: AiRealityCheckOutput,
) -> AiRealityCheckOutput:
    """Keep locked tiers/slugs; take LLM narrative fields."""
    locked = {t.career_slug: t for t in base.tracks}
    merged_tracks: list[CareerTrack] = []

    for et in enriched.tracks:
        bt = locked.get(et.career_slug)
        if not bt:
            continue
        merged_tracks.append(
            bt.model_copy(
                update={
                    "replaces": et.replaces or bt.replaces,
                    "amplifies": et.amplifies or bt.amplifies,
                    "evolved_role_2029": et.evolved_role_2029 or bt.evolved_role_2029,
                    "survival_skills": et.survival_skills or bt.survival_skills,
                }
            )
        )

    if len(merged_tracks) != 3:
        return base

    briefing = enriched.disruption_briefing
    if not briefing.summary.strip():
        briefing = base.disruption_briefing

    return AiRealityCheckOutput(tracks=merged_tracks, disruption_briefing=briefing)


def enrich_with_llm(
    base: AiRealityCheckOutput,
    intake: IntakeForm,
    *,
    api_key: str,
    model: str,
) -> tuple[AiRealityCheckOutput, int, int]:
    import anthropic

    payload = {
        "intake_summary": {
            "interests": [i.value for i in intake.self_assessment.interest_bias],
            "commitment": intake.self_assessment.commitment_slider,
        },
        "locked_output": base.model_dump(mode="json"),
        "tier_definitions": data_registry.load_ai_risk_taxonomy().tier_definitions,
    }

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=3072,
        system=ENRICHMENT_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, default=str)}],
    )
    text = "\n".join(b.text for b in response.content if b.type == "text")
    enriched = AiRealityCheckOutput.model_validate(_extract_json(text))
    merged = _merge_llm_enrichment(base, enriched)
    return merged, response.usage.input_tokens, response.usage.output_tokens
