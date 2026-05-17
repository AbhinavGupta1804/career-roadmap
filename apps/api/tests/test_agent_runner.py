"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_agent_runner.py -q"""

from app.agents.config import AgentName
from app.agents.runner import run_agent
from app.schemas.agents import CareerPathPickerOutput
from app.schemas.intake import (
    BudgetInr,
    CgpaBand,
    CollegeTier,
    HoursPerDay,
    InterestArea,
    PrimaryGoal,
    ProfileBasics,
    RelocationPreference,
    SelfAssessment,
    SkillsAndGoals,
    TargetSalaryBand,
    TechStream,
    TimelineToJob,
    YearOfStudy,
    IntakeForm,
)


def _sample_intake() -> IntakeForm:
    return IntakeForm(
        profile=ProfileBasics(
            year_of_study=YearOfStudy.THIRD,
            stream=TechStream.CS,
            college_tier=CollegeTier.TIER_2,
            cgpa_band=CgpaBand.BAND_7_5_8_5,
            city="Pune",
            relocation=RelocationPreference.YES,
            hours_per_day=HoursPerDay.TWO_TO_THREE,
            budget_inr=BudgetInr.LOW,
        ),
        self_assessment=SelfAssessment(
            coding_comfort=3,
            math_logic_comfort=3,
            communication_comfort=3,
            design_visual_comfort=4,
            people_sales_comfort=2,
            detail_patience=3,
            interest_bias=[
                InterestArea.MACHINE_LEARNING,
                InterestArea.DATA_SCIENCE,
            ],
            commitment_slider=7,
        ),
        skills_and_goals=SkillsAndGoals(
            skills=[],
            has_internship=False,
            primary_goal=PrimaryGoal.FIRST_JOB,
            target_salary_band=TargetSalaryBand.BAND_6_12,
            timeline_to_job=TimelineToJob.TWELVE_MONTHS,
        ),
    )


def test_mock_career_path_picker_returns_valid_json() -> None:
    intake = _sample_intake()
    result = run_agent(
        AgentName.CAREER_PATH_PICKER,
        {
            "intake": intake.model_dump(mode="json"),
            "careers": [],
            "exclude_slugs": [],
        },
    )

    assert result.mock is True
    assert result.cost_inr == 0.0
    assert result.latency_ms >= 0

    parsed = CareerPathPickerOutput.model_validate(result.output)
    assert len(parsed.tracks) == 3
    types = {t.type.value for t in parsed.tracks}
    assert types == {"Stretch", "Realistic", "Safe"}


def test_mock_ai_reality_check_tags_tracks() -> None:
    intake = _sample_intake()
    picker = run_agent(
        AgentName.CAREER_PATH_PICKER,
        {"intake": intake.model_dump(mode="json"), "careers": [], "exclude_slugs": []},
    )
    reality = run_agent(
        AgentName.AI_REALITY_CHECK,
        {
            "intake": intake.model_dump(mode="json"),
            "picker_output": picker.output,
        },
    )

    assert reality.mock is True
    for track in reality.output["tracks"]:
        assert track["ai_risk_tier"] is not None
        assert track["ai_risk_tier"] <= 3
