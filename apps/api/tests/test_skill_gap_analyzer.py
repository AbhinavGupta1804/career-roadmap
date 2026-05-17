"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_skill_gap_analyzer.py -q"""

from app.agents.runner import run_agent
from app.agents.config import AgentName
from app.agents.skill_gap_analyzer import (
    JD_FREQUENCY_THRESHOLD_PCT,
    analyze_skill_gaps,
    build_skill_frequency_map,
    filter_skills_by_threshold,
    skills_per_jd_from_cache,
)
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


def _intake(skills: list[tuple[str, SkillRating]] | None = None) -> IntakeForm:
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
            coding_comfort=4,
            math_logic_comfort=4,
            communication_comfort=3,
            design_visual_comfort=2,
            people_sales_comfort=2,
            detail_patience=4,
            interest_bias=[InterestArea.DATA_SCIENCE, InterestArea.WEB_DEV],
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


def test_data_analyst_frequency_map_matches_corpus() -> None:
    cache = data_registry.load_jd_cache("data-analyst")
    per_jd = skills_per_jd_from_cache(cache)
    assert len(per_jd) == 50

    freq = build_skill_frequency_map(per_jd)
    expected = {"SQL", "Python", "Excel", "Power BI", "Tableau", "Statistics"}
    assert set(freq.keys()) == expected
    assert all(pct == 100.0 for pct in freq.values())

    filtered = filter_skills_by_threshold(freq, JD_FREQUENCY_THRESHOLD_PCT)
    assert {name for name, _ in filtered} == expected


def test_threshold_drops_skills_below_15_percent() -> None:
    # 10 JDs: Common (8/10=80%), SQL (2/10=20%), Rare (1/10=10%)
    skills_per_jd = [
        ["Common", "SQL"],
        ["Common"],
        ["Common"],
        ["Common"],
        ["Common"],
        ["Common"],
        ["Common"],
        ["Common"],
        ["SQL"],
        ["Rare"],
    ]
    freq = build_skill_frequency_map(skills_per_jd)
    assert freq["Common"] == 80.0
    assert freq["SQL"] == 20.0
    assert freq["Rare"] == 10.0

    kept = filter_skills_by_threshold(freq)
    names = {n for n, _ in kept}
    assert "Common" in names
    assert "SQL" in names
    assert "Rare" not in names


def test_analyze_skill_gaps_data_analyst_student_ratings() -> None:
    intake = _intake(
        [
            ("SQL", SkillRating.WITH_HELP),
            ("Python", SkillRating.SOLO),
            ("Excel", SkillRating.HEARD_OF),
        ],
    )
    result = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")

    assert result.career_slug == "data-analyst"
    assert result.role == "Data Analyst"
    skill_names = {s.name for s in result.skills}
    assert skill_names == {"SQL", "Python", "Excel", "Power BI", "Tableau", "Statistics"}

    by_name = {s.name: s for s in result.skills}
    assert by_name["SQL"].current_level == 2
    assert by_name["SQL"].required_level == 4
    assert by_name["SQL"].demand_frequency_pct == 100.0
    assert by_name["SQL"].weeks_to_bridge >= 1

    assert by_name["Python"].current_level == 4
    assert by_name["Python"].weeks_to_bridge == 0

    assert by_name["Excel"].current_level == 1
    assert by_name["Excel"].weeks_to_bridge >= 1

    assert by_name["Power BI"].current_level == 0
    assert by_name["Power BI"].priority in ("must", "should", "nice")


def test_mock_agent_runner_uses_jd_corpus() -> None:
    intake = _intake([("SQL", SkillRating.WITH_HELP)])
    result = run_agent(
        AgentName.SKILL_GAP_ANALYZER,
        {
            "intake": intake.model_dump(mode="json"),
            "career_slug": "data-analyst",
            "role_name": "Data Analyst",
            "jd_summary": {},
            "resources": [],
        },
    )
    assert result.mock is True
    skills = {s["name"] for s in result.output["skills"]}
    assert "SQL" in skills
    assert "Power BI" in skills
    assert all(
        s["demand_frequency_pct"] >= JD_FREQUENCY_THRESHOLD_PCT
        for s in result.output["skills"]
    )
