from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class TrackType(str, Enum):
    STRETCH = "Stretch"
    REALISTIC = "Realistic"
    SAFE = "Safe"


class AiRiskTier(int, Enum):
    TAILWIND = 1
    AUGMENTED = 2
    PARTIAL = 3
    HEAVY = 4
    SUNSET = 5


class CareerTrack(BaseModel):
    name: str
    career_slug: str
    type: TrackType
    why_recommended: str
    avg_starting_salary_band: str
    time_to_job_estimate_months: int = Field(ge=1, le=36)
    competition_level: Literal["low", "medium", "high"]
    top_hiring_companies: list[str] = Field(default_factory=list, max_length=8)
    honest_warning: str | None = None
    ai_risk_tier: AiRiskTier | None = None
    ai_risk_label: str | None = None
    replaces: list[str] = Field(default_factory=list)
    amplifies: list[str] = Field(default_factory=list)
    evolved_role_2029: str | None = None
    survival_skills: list[str] = Field(default_factory=list)


class CareerPathPickerOutput(BaseModel):
    tracks: list[CareerTrack] = Field(min_length=3, max_length=3)


class DisruptionBriefing(BaseModel):
    summary: str
    rejected_paths: list[str] = Field(default_factory=list)
    do_not_pursue_callouts: list[str] = Field(default_factory=list)


class AiRealityCheckOutput(BaseModel):
    tracks: list[CareerTrack] = Field(min_length=3, max_length=3)
    disruption_briefing: DisruptionBriefing


class SkillGapItem(BaseModel):
    name: str
    current_level: int = Field(ge=0, le=5)
    required_level: int = Field(ge=1, le=5)
    demand_frequency_pct: float = Field(ge=0, le=100)
    weeks_to_bridge: int = Field(ge=0, le=52)
    priority: Literal["must", "should", "nice"]


class SkillGapAnalyzerOutput(BaseModel):
    role: str
    career_slug: str
    skills: list[SkillGapItem]


class LearningWeek(BaseModel):
    week: int = Field(ge=1)
    focus_skill: str
    resources: list[str]
    hours: int = Field(ge=1)
    mini_task: str
    checkpoint: bool = False


class LearningPathGeneratorOutput(BaseModel):
    total_weeks: int
    weeks: list[LearningWeek]


class PortfolioProject(BaseModel):
    name: str
    difficulty: Literal["Beginner", "Easy", "Medium", "Hard", "Capstone"]
    problem_statement: str
    dataset_or_api: str | None = None
    expected_output: str
    hours_estimate: int = Field(ge=4)
    tech_stack: list[str]
    resume_bullet: str


class ProjectIdeatorOutput(BaseModel):
    projects: list[PortfolioProject] = Field(min_length=5, max_length=5)


class CertificationItem(BaseModel):
    name: str
    provider: str
    cost: str
    hours: int
    why: str


class CertificationAdvisorOutput(BaseModel):
    recommended: list[CertificationItem]
    skip: list[dict[str, str]]  # {name, why_skip}


class PortfolioSiteSection(BaseModel):
    section: Literal["hero", "about", "projects", "skills", "contact"]
    content: str


class LinkedInPost(BaseModel):
    week: int
    post_type: Literal["project", "learning", "opinion", "resource"]
    template: str


class PortfolioBuilderOutput(BaseModel):
    github_readme_md: str
    portfolio_site_sections: list[PortfolioSiteSection]
    hosting_suggestion: str
    linkedin_calendar: list[LinkedInPost]
    connection_request_templates: list[str] = Field(min_length=5, max_length=5)


class AgentOutputs(BaseModel):
    career_paths: CareerPathPickerOutput | None = None
    ai_reality_check: AiRealityCheckOutput | None = None
    skill_gap: SkillGapAnalyzerOutput | None = None
    learning_path: LearningPathGeneratorOutput | None = None
    projects: ProjectIdeatorOutput | None = None
    certifications: CertificationAdvisorOutput | None = None
    portfolio: PortfolioBuilderOutput | None = None
    chosen_track_type: TrackType | None = None
