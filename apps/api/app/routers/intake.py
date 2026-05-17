from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.intake import IntakeForm
from app.services.supabase_client import SupabaseNotConfiguredError, get_supabase

router = APIRouter(prefix="/intake", tags=["intake"])


class IntakeCreateResponse(BaseModel):
    submission_id: str
    status: str
    created_at: datetime


class IntakeGetResponse(BaseModel):
    submission_id: str
    status: str
    created_at: datetime
    form_data: IntakeForm


@router.post("", response_model=IntakeCreateResponse)
def create_intake_submission(payload: IntakeForm) -> IntakeCreateResponse:
    try:
        client = get_supabase()
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    form_json = payload.model_dump(mode="json")
    try:
        result = (
            client.table("intake_submissions")
            .insert({"form_data": form_json, "status": "submitted"})
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Failed to save intake submission: {exc}",
        ) from exc

    if not result.data:
        raise HTTPException(status_code=502, detail="Supabase returned no row")

    row = result.data[0]
    return IntakeCreateResponse(
        submission_id=row["id"],
        status=row["status"],
        created_at=row["created_at"],
    )


@router.get("/{submission_id}", response_model=IntakeGetResponse)
def get_intake_submission(submission_id: str) -> IntakeGetResponse:
    try:
        client = get_supabase()
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        result = (
            client.table("intake_submissions")
            .select("id, status, created_at, form_data")
            .eq("id", submission_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Failed to load intake submission: {exc}",
        ) from exc

    if not result.data:
        raise HTTPException(status_code=404, detail="Submission not found")

    row = result.data
    return IntakeGetResponse(
        submission_id=row["id"],
        status=row["status"],
        created_at=row["created_at"],
        form_data=IntakeForm.model_validate(row["form_data"]),
    )
