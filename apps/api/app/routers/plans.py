from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.pdf_export import build_plan_pdf, pdf_filename

from app.agents.exceptions import AgentError
from app.agents.orchestrator import (
    generate_initial_tracks,
    generate_mission_plan,
    generate_mission_plan_from_submission,
)
from app.schemas.agents import AgentOutputs, TrackType
from app.schemas.progress import WeekProgress, WeekProgressUpdate
from app.services.plan_repository import get_plan, parse_agent_outputs, update_plan
from app.services.supabase_client import SupabaseNotConfiguredError
from app.services.week_progress import apply_week_toggle, parse_week_progress

router = APIRouter(prefix="/plans", tags=["plans"])


class PlanResponse(BaseModel):
    plan_id: str
    intake_id: str
    status: str
    chosen_track_type: str | None = None
    agent_outputs: AgentOutputs | dict[str, Any] = {}
    week_progress: WeekProgress = Field(default_factory=WeekProgress)
    llm_cost_inr: float = 0
    llm_token_log: list[dict[str, Any]] = Field(default_factory=list)


class SelectTrackRequest(BaseModel):
    track_type: TrackType


def _to_response(row: dict[str, Any]) -> PlanResponse:
    outputs = row.get("agent_outputs") or {}
    try:
        parsed_outputs = parse_agent_outputs(outputs)
    except Exception:
        parsed_outputs = outputs

    return PlanResponse(
        plan_id=row["id"],
        intake_id=row["intake_id"],
        status=row["status"],
        chosen_track_type=row.get("chosen_track_type"),
        agent_outputs=parsed_outputs,
        week_progress=parse_week_progress(row.get("week_progress")),
        llm_cost_inr=float(row.get("llm_cost_inr") or 0),
        llm_token_log=row.get("llm_token_log") or [],
    )


def _total_plan_weeks(outputs: AgentOutputs | dict[str, Any]) -> int:
    if isinstance(outputs, AgentOutputs):
        lp = outputs.learning_path
    else:
        lp = (outputs or {}).get("learning_path")
    if not lp:
        return 0
    if isinstance(lp, dict):
        return int(lp.get("total_weeks") or len(lp.get("weeks") or []))
    return lp.total_weeks


@router.post("/start/{submission_id}", response_model=PlanResponse)
def start_plan(submission_id: str) -> PlanResponse:
    """Run Agent 1 → Agent 2. Pauses at track selection."""
    try:
        row = generate_initial_tracks(submission_id)
        return _to_response(row)
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=exc.user_message) from exc


def _select_track_impl(plan_id: str, track_type: TrackType) -> PlanResponse:
    try:
        row = generate_mission_plan(plan_id, track_type)
        return _to_response(row)
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=exc.user_message) from exc


@router.get("/by-intake/{intake_id}", response_model=PlanResponse)
def get_plan_by_intake(intake_id: str) -> PlanResponse:
    from app.services.plan_repository import get_plan_by_intake

    row = get_plan_by_intake(intake_id)
    if not row:
        raise HTTPException(status_code=404, detail="No mission plan for this intake")
    return _to_response(row)


@router.post("/{plan_id}/select-track", response_model=PlanResponse)
def select_track_post(plan_id: str, body: SelectTrackRequest) -> PlanResponse:
    """After student picks a track: run Agents 3–5 (6–7 stubbed)."""
    return _select_track_impl(plan_id, body.track_type)


@router.patch("/{plan_id}/track", response_model=PlanResponse)
def select_track_patch(plan_id: str, body: SelectTrackRequest) -> PlanResponse:
    """REST alias for track selection (triggers Agents 3–5)."""
    return _select_track_impl(plan_id, body.track_type)


@router.post("/generate/{submission_id}", response_model=PlanResponse)
def generate_full(submission_id: str, track_type: TrackType = TrackType.REALISTIC) -> PlanResponse:
    """Dev helper: run full mock pipeline in one call."""
    try:
        row = generate_mission_plan_from_submission(submission_id, track_type)
        return _to_response(row)
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=exc.user_message) from exc


def _pdf_response(plan: PlanResponse) -> Response:
    if plan.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Mission plan is not complete yet. Finish track selection first.",
        )
    track = None
    outputs = plan.agent_outputs
    if isinstance(outputs, AgentOutputs) and outputs.ai_reality_check and plan.chosen_track_type:
        for t in outputs.ai_reality_check.tracks:
            if t.type.value == plan.chosen_track_type:
                track = t
                break

    role_name = track.name if track else (outputs.skill_gap.role if isinstance(outputs, AgentOutputs) and outputs.skill_gap else None)
    pdf_bytes = build_plan_pdf(
        chosen_track_type=plan.chosen_track_type,
        agent_outputs=plan.agent_outputs,
    )
    filename = pdf_filename(plan.plan_id, role_name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{plan_id}/export.pdf")
def export_plan_pdf(plan_id: str) -> Response:
    """Download mission plan as PDF."""
    try:
        plan = _to_response(get_plan(plan_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _pdf_response(plan)


@router.post("/export-pdf")
def export_plan_pdf_from_body(plan: PlanResponse) -> Response:
    """Download PDF from plan payload (demo / client-side preview)."""
    return _pdf_response(plan)


@router.get("/{plan_id}/progress", response_model=WeekProgress)
def get_week_progress(plan_id: str) -> WeekProgress:
    try:
        row = get_plan(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return parse_week_progress(row.get("week_progress"))


@router.patch("/{plan_id}/progress", response_model=WeekProgress)
def update_week_progress(plan_id: str, body: WeekProgressUpdate) -> WeekProgress:
    try:
        row = get_plan(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if row.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail="Complete your mission plan before tracking weekly progress.",
        )

    outputs = parse_agent_outputs(row.get("agent_outputs") or {})
    total_weeks = _total_plan_weeks(outputs)
    if total_weeks < 1:
        raise HTTPException(status_code=400, detail="No learning plan weeks to track.")

    progress = parse_week_progress(row.get("week_progress"))
    try:
        updated = apply_week_toggle(
            progress,
            week=body.week,
            done=body.done,
            total_weeks=total_weeks,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    update_plan(plan_id, week_progress=updated.model_dump(mode="json"))
    return updated


@router.get("/{plan_id}", response_model=PlanResponse)
def get_mission_plan(plan_id: str) -> PlanResponse:
    try:
        return _to_response(get_plan(plan_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
