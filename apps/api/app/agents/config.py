from dataclasses import dataclass
from enum import Enum
from typing import Type

from pydantic import BaseModel

from app.schemas.agents import (
    AiRealityCheckOutput,
    CareerPathPickerOutput,
    CertificationAdvisorOutput,
    LearningPathGeneratorOutput,
    PortfolioBuilderOutput,
    ProjectIdeatorOutput,
    SkillGapAnalyzerOutput,
)


class AgentName(str, Enum):
    CAREER_PATH_PICKER = "career_path_picker"
    AI_REALITY_CHECK = "ai_reality_check"
    SKILL_GAP_ANALYZER = "skill_gap_analyzer"
    LEARNING_PATH_GENERATOR = "learning_path_generator"
    PROJECT_IDEATOR = "project_ideator"
    CERTIFICATION_ADVISOR = "certification_advisor"
    PORTFOLIO_BUILDER = "portfolio_builder"


class AgentModel(str, Enum):
    SONNET = "claude-sonnet-4-20250514"
    HAIKU = "claude-3-5-haiku-20241022"


@dataclass(frozen=True)
class AgentSpec:
    name: AgentName
    default_model: AgentModel
    output_schema: Type[BaseModel]
    description: str


AGENT_SPECS: dict[AgentName, AgentSpec] = {
    AgentName.CAREER_PATH_PICKER: AgentSpec(
        name=AgentName.CAREER_PATH_PICKER,
        default_model=AgentModel.SONNET,
        output_schema=CareerPathPickerOutput,
        description="Pick 3 career tracks (Stretch / Realistic / Safe)",
    ),
    AgentName.AI_REALITY_CHECK: AgentSpec(
        name=AgentName.AI_REALITY_CHECK,
        default_model=AgentModel.SONNET,
        output_schema=AiRealityCheckOutput,
        description="Tag careers with AI disruption tiers",
    ),
    AgentName.SKILL_GAP_ANALYZER: AgentSpec(
        name=AgentName.SKILL_GAP_ANALYZER,
        default_model=AgentModel.HAIKU,
        output_schema=SkillGapAnalyzerOutput,
        description="Compare student skills vs JD demand",
    ),
    AgentName.LEARNING_PATH_GENERATOR: AgentSpec(
        name=AgentName.LEARNING_PATH_GENERATOR,
        default_model=AgentModel.SONNET,
        output_schema=LearningPathGeneratorOutput,
        description="Week-by-week learning plan",
    ),
    AgentName.PROJECT_IDEATOR: AgentSpec(
        name=AgentName.PROJECT_IDEATOR,
        default_model=AgentModel.SONNET,
        output_schema=ProjectIdeatorOutput,
        description="Portfolio project ideas",
    ),
    AgentName.CERTIFICATION_ADVISOR: AgentSpec(
        name=AgentName.CERTIFICATION_ADVISOR,
        default_model=AgentModel.HAIKU,
        output_schema=CertificationAdvisorOutput,
        description="JD-backed cert recommendations and skip list",
    ),
    AgentName.PORTFOLIO_BUILDER: AgentSpec(
        name=AgentName.PORTFOLIO_BUILDER,
        default_model=AgentModel.SONNET,
        output_schema=PortfolioBuilderOutput,
        description="GitHub README, portfolio site, LinkedIn calendar, outreach",
    ),
}
