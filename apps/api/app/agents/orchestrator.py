from __future__ import annotations

import concurrent.futures
from typing import Any

from app.agents.ai_reality_check import (
    assert_plan_safe,
    tracks_requiring_repick,
)
from app.agents.config import AgentName
from app.agents.exceptions import AgentError
from app.agents.runner import AgentRunResult, run_agent
from app.schemas.agents import (
    AgentOutputs,
    AiRealityCheckOutput,
    CareerPathPickerOutput,
    TrackType,
)
from app.schemas.intake import IntakeForm
from app.services import data_registry, plan_repository


def _log_entry(result: AgentRunResult) -> dict[str, Any]:
    return {
        "agent": result.agent_name,
        "model": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "cost_inr": result.cost_inr,
        "latency_ms": result.latency_ms,
        "mock": result.mock,
    }


def _merge_outputs(plan: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    outputs = dict(plan.get("agent_outputs") or {})
    outputs.update(patch)
    return outputs


def _total_cost(log: list[dict[str, Any]]) -> float:
    return round(sum(entry.get("cost_inr", 0) for entry in log), 2)


def _run_agents_1_and_2(
    intake: IntakeForm,
    token_log: list[dict[str, Any]],
) -> tuple[CareerPathPickerOutput, AiRealityCheckOutput]:
    exclude_slugs: set[str] = set()
    picker_output: CareerPathPickerOutput | None = None
    reality_output: AiRealityCheckOutput | None = None

    for attempt in range(3):  # initial + 2 re-picks
        picker_result = run_agent(
            AgentName.CAREER_PATH_PICKER,
            {
                "intake": intake.model_dump(mode="json"),
                "careers": [
                    c.model_dump(mode="json")
                    for c in data_registry.load_career_taxonomy().careers
                ],
                "exclude_slugs": list(exclude_slugs),
            },
        )
        token_log.append(_log_entry(picker_result))
        picker_output = CareerPathPickerOutput.model_validate(picker_result.output)

        reality_result = run_agent(
            AgentName.AI_REALITY_CHECK,
            {
                "intake": intake.model_dump(mode="json"),
                "picker_output": picker_output.model_dump(mode="json"),
                "ai_risk_taxonomy": data_registry.load_ai_risk_taxonomy().model_dump(
                    mode="json"
                ),
            },
        )
        token_log.append(_log_entry(reality_result))
        reality_output = AiRealityCheckOutput.model_validate(reality_result.output)

        bad = tracks_requiring_repick(reality_output.tracks)
        if not bad:
            assert_plan_safe(reality_output)
            return picker_output, reality_output

        exclude_slugs.update(t.career_slug for t in bad)
        rejected_names = [f"{t.name} (Tier {t.ai_risk_tier.value})" for t in bad if t.ai_risk_tier]

        if attempt == 2:
            safe_tracks = [
                t
                for t in reality_output.tracks
                if t.ai_risk_tier and t.ai_risk_tier.value not in (4, 5)
            ]
            if len(safe_tracks) < 3:
                raise AgentError(
                    "ai_reality_check",
                    "Could not find 3 tier-safe career paths",
                    user_message=(
                        "We couldn't find three safe career paths for your profile. "
                        "Try adjusting your interests."
                    ),
                )
            from app.agents.ai_reality_check import apply_reality_check

            reality_output = apply_reality_check(
                CareerPathPickerOutput(tracks=safe_tracks[:3]),
                intake,
                rejected_paths=rejected_names,
            )
            assert_plan_safe(reality_output)
            picker_output = CareerPathPickerOutput(tracks=reality_output.tracks)
            return picker_output, reality_output

    raise AgentError("career_path_picker", "Exhausted re-pick attempts")


def generate_initial_tracks(submission_id: str) -> dict[str, Any]:
    """
    Agent 1 → Agent 2. Persists plan with status awaiting_track_choice.
    """
    intake = plan_repository.load_intake(submission_id)
    existing = plan_repository.get_plan_by_intake(submission_id)
    plan = existing or plan_repository.create_plan(submission_id)
    plan_id = plan["id"]

    plan_repository.update_plan(plan_id, status="picking_tracks")
    token_log: list[dict[str, Any]] = list(plan.get("llm_token_log") or [])

    try:
        picker_output, reality_output = _run_agents_1_and_2(intake, token_log)
        outputs = AgentOutputs(
            career_paths=picker_output,
            ai_reality_check=reality_output,
        )
        updated = plan_repository.update_plan(
            plan_id,
            status="awaiting_track_choice",
            agent_outputs=outputs.model_dump(mode="json"),
            llm_cost_inr=_total_cost(token_log),
            llm_token_log=token_log,
        )
        plan_repository.update_intake_status(submission_id, "tracks_ready")
        return updated
    except AgentError:
        plan_repository.update_plan(plan_id, status="failed", llm_token_log=token_log)
        raise


def _chosen_track(
    outputs: AgentOutputs,
    track_type: TrackType,
):
    if not outputs.ai_reality_check:
        raise AgentError(
            "orchestrator",
            "Missing AI reality check output",
        )
    for track in outputs.ai_reality_check.tracks:
        if track.type == track_type:
            return track
    raise AgentError(
        "orchestrator",
        f"Track type {track_type} not found",
        user_message="Selected track not found. Please pick again.",
    )


def _run_parallel_deep_agents(
    intake: IntakeForm,
    track,
    token_log: list[dict[str, Any]],
) -> dict[str, Any]:
    jd_summary: dict[str, Any] = {}
    try:
        jd_cache = data_registry.load_jd_cache(track.career_slug)
        jd_summary = {
            "role_slug": jd_cache.role_slug,
            "jd_count": len(jd_cache.jds),
            "top_skills": jd_cache.jds[0].skills_mentioned if jd_cache.jds else [],
        }
    except FileNotFoundError:
        jd_summary = {"role_slug": track.career_slug, "jd_count": 0, "top_skills": []}

    resource_payload = [
        r.model_dump(mode="json")
        for r in data_registry.load_resource_library().resources
    ]

    base_input = {
        "intake": intake.model_dump(mode="json"),
        "career_slug": track.career_slug,
        "role_name": track.name,
        "jd_summary": jd_summary,
        "resources": resource_payload,
    }

    # Agent 3 first — Agents 4 & 5 consume skill_gap output
    skill_gap_result = run_agent(AgentName.SKILL_GAP_ANALYZER, base_input)
    token_log.append(_log_entry(skill_gap_result))
    enriched_input = {**base_input, "skill_gap": skill_gap_result.output}

    tasks = {
        AgentName.LEARNING_PATH_GENERATOR: lambda: run_agent(
            AgentName.LEARNING_PATH_GENERATOR, enriched_input
        ),
        AgentName.PROJECT_IDEATOR: lambda: run_agent(
            AgentName.PROJECT_IDEATOR, enriched_input
        ),
        AgentName.CERTIFICATION_ADVISOR: lambda: run_agent(
            AgentName.CERTIFICATION_ADVISOR, base_input
        ),
    }

    results: dict[str, AgentRunResult] = {
        AgentName.SKILL_GAP_ANALYZER: skill_gap_result,
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fn): name for name, fn in tasks.items()}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            results[name] = future.result()

    patch: dict[str, Any] = {"skill_gap": skill_gap_result.output}
    for name, result in results.items():
        if name == AgentName.SKILL_GAP_ANALYZER:
            continue
        token_log.append(_log_entry(result))
        if name == AgentName.LEARNING_PATH_GENERATOR:
            patch["learning_path"] = result.output
        elif name == AgentName.PROJECT_IDEATOR:
            patch["projects"] = result.output
        elif name == AgentName.CERTIFICATION_ADVISOR:
            patch["certifications"] = result.output

    if "certifications" not in patch:
        patch["certifications"] = {"recommended": [], "skip": []}

    portfolio_input = {
        **enriched_input,
        "learning_path": patch.get("learning_path"),
        "projects": patch.get("projects"),
        "certifications": patch.get("certifications"),
        "top_hiring_companies": track.top_hiring_companies,
    }
    portfolio_result = run_agent(AgentName.PORTFOLIO_BUILDER, portfolio_input)
    token_log.append(_log_entry(portfolio_result))
    patch["portfolio"] = portfolio_result.output

    return patch


def generate_mission_plan(plan_id: str, track_type: TrackType) -> dict[str, Any]:
    """
    After track selection: Agent 3, then Agents 4–6 in parallel, then Agent 7.
    """
    plan = plan_repository.get_plan(plan_id)
    intake_id = plan["intake_id"]
    intake = plan_repository.load_intake(intake_id)

    outputs = plan_repository.parse_agent_outputs(plan.get("agent_outputs") or {})
    track = _chosen_track(outputs, track_type)

    plan_repository.update_plan(
        plan_id,
        status="generating",
        chosen_track_type=track_type,
    )
    token_log: list[dict[str, Any]] = list(plan.get("llm_token_log") or [])

    try:
        deep_patch = _run_parallel_deep_agents(intake, track, token_log)
        merged = _merge_outputs(
            plan,
            {
                **outputs.model_dump(mode="json"),
                **deep_patch,
                "chosen_track_type": track_type.value,
            },
        )
        final_outputs = AgentOutputs.model_validate(merged)

        updated = plan_repository.update_plan(
            plan_id,
            status="completed",
            chosen_track_type=track_type,
            agent_outputs=final_outputs.model_dump(mode="json"),
            llm_cost_inr=_total_cost(token_log),
            llm_token_log=token_log,
        )
        plan_repository.update_intake_status(intake_id, "completed")
        return updated
    except AgentError:
        plan_repository.update_plan(plan_id, status="failed", llm_token_log=token_log)
        raise


def generate_mission_plan_from_submission(
    submission_id: str,
    track_type: TrackType = TrackType.REALISTIC,
) -> dict[str, Any]:
    """
    Full pipeline for testing: initial tracks (if needed) + track selection + deep agents.
  """
    plan = plan_repository.get_plan_by_intake(submission_id)
    if not plan or plan.get("status") in ("pending", "failed"):
        plan = generate_initial_tracks(submission_id)
    elif plan.get("status") == "picking_tracks":
        plan = generate_initial_tracks(submission_id)

    if plan.get("status") == "awaiting_track_choice":
        return generate_mission_plan(plan["id"], track_type)

    if plan.get("status") == "completed":
        return plan

    return generate_mission_plan(plan["id"], track_type)
