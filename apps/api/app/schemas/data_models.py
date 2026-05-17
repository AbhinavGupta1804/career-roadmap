from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.agents import AiRiskTier


class SalaryBand(BaseModel):
    min_lpa: float
    max_lpa: float


class CareerEntry(BaseModel):
    slug: str
    name: str
    interest_tags: list[str] = Field(min_length=1)
    required_skills: list[str] = Field(min_length=1)
    salary_bands: dict[Literal["tier_1", "tier_2", "tier_3"], SalaryBand]
    market_demand_index: float = Field(ge=0, le=1)
    ai_resilience_index: float = Field(ge=0, le=1)
    competition_level: Literal["low", "medium", "high"]
    typical_months_to_job: int = Field(ge=3, le=24)
    entry_difficulty: Literal["low", "medium", "high"]


class CareerTaxonomy(BaseModel):
    version: str
    careers: list[CareerEntry] = Field(min_length=1)


class TierDefinition(BaseModel):
    label: str
    description: str


class CareerRiskProfile(BaseModel):
    tier: AiRiskTier
    replaces: list[str] = Field(default_factory=list)
    amplifies: list[str] = Field(default_factory=list)
    evolved_role_2029: str
    survival_skills: list[str] = Field(default_factory=list)


class AiRiskTaxonomy(BaseModel):
    version: str
    tier_definitions: dict[str, TierDefinition]
    careers: dict[str, CareerRiskProfile]


class JobDescription(BaseModel):
    id: str
    role_slug: str
    title: str
    company: str
    location: str
    experience_level: Literal["fresher", "0-1", "intern"]
    description: str
    skills_mentioned: list[str] = Field(default_factory=list)
    certifications_mentioned: list[str] = Field(default_factory=list)


class RoleJdCache(BaseModel):
    role_slug: str
    role_name: str
    jds: list[JobDescription] = Field(min_length=1)


class LearningResource(BaseModel):
    id: str
    title: str
    url: str
    type: Literal["video", "course", "doc", "book"]
    cost: Literal["free", "paid"]
    cost_inr_max: int = Field(ge=0)
    hours: int = Field(ge=1)
    skills_taught: list[str] = Field(min_length=1)
    provider: str | None = None


class ResourceLibrary(BaseModel):
    version: str
    resources: list[LearningResource] = Field(min_length=1)
