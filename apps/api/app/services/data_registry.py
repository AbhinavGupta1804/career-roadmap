import json
from functools import lru_cache
from pathlib import Path

from app.schemas.data_models import (
    AiRiskTaxonomy,
    CareerTaxonomy,
    ResourceLibrary,
    RoleJdCache,
)


def _repo_data_dir() -> Path:
    # apps/api/app/services -> repo root is 4 levels up
    return Path(__file__).resolve().parents[4] / "data"


@lru_cache
def load_career_taxonomy() -> CareerTaxonomy:
    path = _repo_data_dir() / "careers.json"
    return CareerTaxonomy.model_validate_json(path.read_text(encoding="utf-8"))


@lru_cache
def load_ai_risk_taxonomy() -> AiRiskTaxonomy:
    path = _repo_data_dir() / "ai-risk-tiers.json"
    return AiRiskTaxonomy.model_validate_json(path.read_text(encoding="utf-8"))


@lru_cache
def load_resource_library() -> ResourceLibrary:
    path = _repo_data_dir() / "resources.json"
    return ResourceLibrary.model_validate_json(path.read_text(encoding="utf-8"))


def list_jd_role_slugs() -> list[str]:
    jds_dir = _repo_data_dir() / "jds"
    if not jds_dir.exists():
        return []
    return sorted(path.stem for path in jds_dir.glob("*.json"))


@lru_cache
def load_jd_cache(role_slug: str) -> RoleJdCache:
    path = _repo_data_dir() / "jds" / f"{role_slug}.json"
    if not path.exists():
        raise FileNotFoundError(f"No JD cache for role: {role_slug}")
    return RoleJdCache.model_validate_json(path.read_text(encoding="utf-8"))


def load_all_jd_caches() -> dict[str, RoleJdCache]:
    return {slug: load_jd_cache(slug) for slug in list_jd_role_slugs()}


def validate_seed_data() -> dict:
    careers = load_career_taxonomy()
    risks = load_ai_risk_taxonomy()
    resources = load_resource_library()
    jd_slugs = list_jd_role_slugs()
    jd_caches = load_all_jd_caches()

    career_slugs = {c.slug for c in careers.careers}
    risk_slugs = set(risks.careers.keys())
    missing_risk = career_slugs - risk_slugs
    extra_risk = risk_slugs - career_slugs

    return {
        "careers_count": len(careers.careers),
        "ai_risk_profiles_count": len(risks.careers),
        "resources_count": len(resources.resources),
        "jd_roles_count": len(jd_slugs),
        "jd_total_count": sum(len(cache.jds) for cache in jd_caches.values()),
        "career_slugs_missing_risk_profile": sorted(missing_risk),
        "risk_profiles_without_career": sorted(extra_risk),
        "data_valid": not missing_risk and not extra_risk,
    }
