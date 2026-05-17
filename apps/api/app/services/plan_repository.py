from __future__ import annotations

from typing import Any

from app.schemas.agents import AgentOutputs, TrackType
from app.schemas.intake import IntakeForm
from app.services.supabase_client import get_supabase


def _client():
    return get_supabase()


def load_intake(submission_id: str) -> IntakeForm:
    result = (
        _client()
        .table("intake_submissions")
        .select("form_data")
        .eq("id", submission_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise ValueError(f"Intake submission not found: {submission_id}")
    return IntakeForm.model_validate(result.data["form_data"])


def create_plan(intake_id: str) -> dict[str, Any]:
    result = (
        _client()
        .table("mission_plans")
        .insert(
            {
                "intake_id": intake_id,
                "status": "pending",
                "agent_outputs": {},
                "llm_cost_inr": 0,
                "llm_token_log": [],
            }
        )
        .execute()
    )
    if not result.data:
        raise RuntimeError("Failed to create mission plan")
    return result.data[0]


def get_plan(plan_id: str) -> dict[str, Any]:
    result = (
        _client()
        .table("mission_plans")
        .select("*")
        .eq("id", plan_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise ValueError(f"Mission plan not found: {plan_id}")
    return result.data


def get_plan_by_intake(intake_id: str) -> dict[str, Any] | None:
    result = (
        _client()
        .table("mission_plans")
        .select("*")
        .eq("intake_id", intake_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]


def update_plan(
    plan_id: str,
    *,
    status: str | None = None,
    chosen_track_type: TrackType | None = None,
    agent_outputs: dict[str, Any] | None = None,
    week_progress: dict[str, Any] | None = None,
    llm_cost_inr: float | None = None,
    llm_token_log: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    if status is not None:
        patch["status"] = status
    if chosen_track_type is not None:
        patch["chosen_track_type"] = chosen_track_type.value
    if agent_outputs is not None:
        patch["agent_outputs"] = agent_outputs
    if week_progress is not None:
        patch["week_progress"] = week_progress
    if llm_cost_inr is not None:
        patch["llm_cost_inr"] = llm_cost_inr
    if llm_token_log is not None:
        patch["llm_token_log"] = llm_token_log

    result = (
        _client().table("mission_plans").update(patch).eq("id", plan_id).execute()
    )
    if not result.data:
        raise RuntimeError(f"Failed to update plan {plan_id}")
    return result.data[0]


def parse_agent_outputs(raw: dict[str, Any]) -> AgentOutputs:
    return AgentOutputs.model_validate(raw)


def update_intake_status(intake_id: str, status: str) -> None:
    _client().table("intake_submissions").update({"status": status}).eq(
        "id", intake_id
    ).execute()
