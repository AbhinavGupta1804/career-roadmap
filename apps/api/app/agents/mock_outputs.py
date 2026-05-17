"""Deterministic mock agent outputs for dev / when AGENT_MOCK_MODE=true."""

from __future__ import annotations

from app.schemas.agents import (
    AiRealityCheckOutput,
    CareerPathPickerOutput,
    CertificationAdvisorOutput,
    LearningPathGeneratorOutput,
    PortfolioBuilderOutput,
    ProjectIdeatorOutput,
    SkillGapAnalyzerOutput,
)
from app.schemas.intake import IntakeForm
from app.services import data_registry


def mock_career_path_picker(
    intake: IntakeForm,
    exclude_slugs: set[str] | None = None,
) -> CareerPathPickerOutput:
    from app.agents.career_path_picker import build_tracks

    return build_tracks(intake, exclude_slugs)


def mock_ai_reality_check(
    picker_output: CareerPathPickerOutput,
    intake: IntakeForm | None = None,
) -> AiRealityCheckOutput:
    from app.agents.ai_reality_check import apply_reality_check

    if intake is None:
        raise ValueError("intake required for AI reality check")
    return apply_reality_check(picker_output, intake)


def mock_skill_gap(
    intake: IntakeForm,
    career_slug: str,
    role_name: str,
) -> SkillGapAnalyzerOutput:
    from app.agents.skill_gap_analyzer import analyze_skill_gaps

    return analyze_skill_gaps(intake, career_slug, role_name)


def mock_learning_path(
    intake: IntakeForm,
    career_slug: str,
    *,
    skill_gap: SkillGapAnalyzerOutput | None = None,
) -> LearningPathGeneratorOutput:
    from app.agents.learning_path_generator import generate_learning_path

    return generate_learning_path(
        intake,
        career_slug,
        skill_gap=skill_gap,
    )


def mock_projects(
    intake: IntakeForm,
    career_slug: str,
    role_name: str,
    *,
    skill_gap: SkillGapAnalyzerOutput | None = None,
) -> ProjectIdeatorOutput:
    from app.agents.project_ideator import generate_projects

    return generate_projects(
        career_slug,
        role_name,
        skill_gap=skill_gap,
    )


def mock_certifications(
    intake: IntakeForm,
    career_slug: str,
) -> CertificationAdvisorOutput:
    from app.agents.certification_advisor import advise_certifications

    return advise_certifications(intake, career_slug)


def mock_portfolio(
    intake: IntakeForm,
    career_slug: str,
    role_name: str,
    *,
    projects: ProjectIdeatorOutput | None = None,
    learning_path: LearningPathGeneratorOutput | None = None,
    skill_gap: SkillGapAnalyzerOutput | None = None,
    certifications: CertificationAdvisorOutput | None = None,
    top_hiring_companies: list[str] | None = None,
) -> PortfolioBuilderOutput:
    from app.agents.portfolio_builder import build_portfolio

    return build_portfolio(
        intake,
        career_slug,
        role_name,
        projects=projects,
        learning_path=learning_path,
        skill_gap=skill_gap,
        certifications=certifications,
        top_hiring_companies=top_hiring_companies,
    )
