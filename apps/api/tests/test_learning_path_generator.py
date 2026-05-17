"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_learning_path_generator.py -q"""

from app.agents.learning_path_generator import (
    TIMELINE_WEEKS,
    generate_learning_path,
    order_gaps_by_dependency,
    pick_resources_for_skill,
    total_weeks_for_student,
)
from app.agents.skill_gap_analyzer import analyze_skill_gaps
from app.agents.runner import run_agent
from app.agents.config import AgentName
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
    StudentSkill,
    SkillRating,
    TargetSalaryBand,
    TechStream,
    TimelineToJob,
    YearOfStudy,
    IntakeForm,
)
from app.services import data_registry


def _intake(
    *,
    hours: HoursPerDay = HoursPerDay.TWO_TO_THREE,
    budget: BudgetInr = BudgetInr.LOW,
    skills: list[tuple[str, SkillRating]] | None = None,
) -> IntakeForm:
    return IntakeForm(
        profile=ProfileBasics(
            year_of_study=YearOfStudy.THIRD,
            stream=TechStream.CS,
            college_tier=CollegeTier.TIER_2,
            cgpa_band=CgpaBand.BAND_7_5_8_5,
            city="Pune",
            relocation=RelocationPreference.YES,
            hours_per_day=hours,
            budget_inr=budget,
        ),
        self_assessment=SelfAssessment(
            coding_comfort=4,
            math_logic_comfort=4,
            communication_comfort=3,
            design_visual_comfort=2,
            people_sales_comfort=2,
            detail_patience=4,
            interest_bias=[InterestArea.DATA_SCIENCE],
            commitment_slider=7,
        ),
        skills_and_goals=SkillsAndGoals(
            skills=[
                StudentSkill(name=name, rating=rating)
                for name, rating in (skills or [])
            ],
            has_internship=False,
            primary_goal=PrimaryGoal.FIRST_JOB,
            target_salary_band=TargetSalaryBand.BAND_6_12,
            timeline_to_job=TimelineToJob.SIX_MONTHS,
        ),
    )


def test_timeline_weeks_by_hours_per_day() -> None:
    assert total_weeks_for_student(HoursPerDay.ONE) == TIMELINE_WEEKS[HoursPerDay.ONE] == 26
    assert total_weeks_for_student(HoursPerDay.TWO_TO_THREE) == 12
    assert total_weeks_for_student(HoursPerDay.FOUR_PLUS) == 8


def test_dependency_order_sql_before_power_bi() -> None:
    intake = _intake()
    gaps = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")
    ordered = order_gaps_by_dependency(gaps.skills)
    names = [g.name for g in ordered]
    assert names.index("SQL") < names.index("Power BI")


def test_twelve_week_plan_data_analyst_student() -> None:
    intake = _intake(
        hours=HoursPerDay.TWO_TO_THREE,
        budget=BudgetInr.LOW,
        skills=[
            ("SQL", SkillRating.WITH_HELP),
            ("Python", SkillRating.SOLO),
            ("Excel", SkillRating.HEARD_OF),
        ],
    )
    gaps = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")
    plan = generate_learning_path(intake, "data-analyst", skill_gap=gaps)

    assert plan.total_weeks == 12
    assert len(plan.weeks) == 12
    assert plan.weeks[0].week == 1
    assert plan.weeks[-1].week == 12

    focus_skills = {w.focus_skill for w in plan.weeks}
    assert "SQL" in focus_skills or "Excel" in focus_skills
    assert any(w.checkpoint for w in plan.weeks)
    assert plan.weeks[-1].checkpoint is True

    for week in plan.weeks:
        assert week.hours == 10
        assert len(week.resources) >= 1
        assert week.mini_task


def test_resources_respect_low_budget() -> None:
    library = data_registry.load_resource_library().resources
    titles = pick_resources_for_skill("SQL", library, BudgetInr.LOW)
    assert titles
    for title in titles:
        matched = next(
            (r for r in library if r.title in title),
            None,
        )
        if matched:
            assert matched.cost == "free"
            assert matched.cost_inr_max <= 2_000


def test_runner_agent4_with_skill_gap_payload() -> None:
    intake = _intake(hours=HoursPerDay.TWO_TO_THREE)
    gaps = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")
    result = run_agent(
        AgentName.LEARNING_PATH_GENERATOR,
        {
            "intake": intake.model_dump(mode="json"),
            "career_slug": "data-analyst",
            "role_name": "Data Analyst",
            "skill_gap": gaps.model_dump(mode="json"),
            "resources": [
                r.model_dump(mode="json")
                for r in data_registry.load_resource_library().resources
            ],
        },
    )
    assert result.mock is True
    assert result.output["total_weeks"] == 12
    assert len(result.output["weeks"]) == 12
