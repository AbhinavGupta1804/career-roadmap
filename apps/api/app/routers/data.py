from fastapi import APIRouter, HTTPException

from app.schemas.data_models import CareerEntry, RoleJdCache
from app.services import data_registry

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/status")
def data_status() -> dict:
    try:
        return data_registry.validate_seed_data()
    except Exception as exc:  # noqa: BLE001 — surface validation errors in dev
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/careers")
def list_careers() -> list[CareerEntry]:
    return data_registry.load_career_taxonomy().careers


@router.get("/careers/{slug}")
def get_career(slug: str) -> CareerEntry:
    for career in data_registry.load_career_taxonomy().careers:
        if career.slug == slug:
            return career
    raise HTTPException(status_code=404, detail=f"Career not found: {slug}")


@router.get("/jds/{role_slug}")
def get_jds(role_slug: str) -> RoleJdCache:
    try:
        return data_registry.load_jd_cache(role_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
