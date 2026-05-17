"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_career_path_picker.py -q"""

from app.agents.career_path_picker import (
    build_candidate_pool,
    build_tracks,
    pick_track_assignments,
)
from app.agents.runner import run_agent
from app.agents.config import AgentName
from app.schemas.agents import CareerPathPickerOutput, TrackType
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


def _intake(
    *,
    stream: TechStream = TechStream.CS,
    interests: list[InterestArea] | None = None,
    commitment: int = 7,
    skills: list[tuple[str, SkillRating]] | None = None,
) -> IntakeForm:
    return IntakeForm(
        profile=ProfileBasics(
            year_of_study=YearOfStudy.THIRD,
            stream=stream,
            college_tier=CollegeTier.TIER_2,
            cgpa_band=CgpaBand.BAND_7_5_8_5,
            city="Pune",
            relocation=RelocationPreference.YES,
            hours_per_day=HoursPerDay.TWO_TO_THREE,
            budget_inr=BudgetInr.LOW,
        ),
        self_assessment=SelfAssessment(
            coding_comfort=4,
            math_logic_comfort=3,
            communication_comfort=3,
            design_visual_comfort=3,
            people_sales_comfort=2,
            detail_patience=3,
            interest_bias=interests
            or [InterestArea.MACHINE_LEARNING, InterestArea.DATA_SCIENCE],
            commitment_slider=commitment,
        ),
        skills_and_goals=SkillsAndGoals(
            skills=[
                StudentSkill(name=n, rating=r)
                for n, r in (skills or [("Python", SkillRating.SOLO), ("SQL", SkillRating.WITH_HELP)])
            ],
            has_internship=False,
            primary_goal=PrimaryGoal.FIRST_JOB,
            target_salary_band=TargetSalaryBand.BAND_6_12,
            timeline_to_job=TimelineToJob.TWELVE_MONTHS,
        ),
    )


def test_same_intake_produces_three_distinct_track_types() -> None:
    intake = _intake()
    a = build_tracks(intake)
    b = build_tracks(intake)

    assert len(a.tracks) == 3
    assert len(b.tracks) == 3
    types_a = {t.type for t in a.tracks}
    types_b = {t.type for t in b.tracks}
    assert types_a == {TrackType.STRETCH, TrackType.REALISTIC, TrackType.SAFE}
    assert types_a == types_b
    slugs_a = {t.career_slug for t in a.tracks}
    slugs_b = {t.career_slug for t in b.tracks}
    assert slugs_a == slugs_b
    assert len(slugs_a) == 3


def test_commitment_splits_pool() -> None:
    high = build_candidate_pool(_intake(commitment=8))
    low = build_candidate_pool(_intake(commitment=2))
    aligned_high = sum(1 for s in high if s.is_interest_aligned)
    aligned_low = sum(1 for s in low if s.is_interest_aligned)
    assert aligned_high >= aligned_low


def test_exclude_slugs_removes_careers() -> None:
    intake = _intake()
    base = build_tracks(intake)
    slug = base.tracks[0].career_slug
    excluded = build_tracks(intake, exclude_slugs={slug})
    assert slug not in {t.career_slug for t in excluded.tracks}


def test_commerce_branch_in_intake_schema() -> None:
    intake = _intake(
        stream=TechStream.COMMERCE,
        interests=[
            InterestArea.FINANCE_ACCOUNTING,
            InterestArea.BUSINESS_ANALYST,
            InterestArea.DIGITAL_MARKETING,
        ],
        skills=[("Excel", SkillRating.SOLO), ("SQL", SkillRating.WITH_HELP)],
    )
    assert intake.profile.stream == TechStream.COMMERCE


def test_commerce_student_pool_includes_business_roles() -> None:
    intake = _intake(
        stream=TechStream.COMMERCE,
        interests=[
            InterestArea.FINANCE_ACCOUNTING,
            InterestArea.BUSINESS_ANALYST,
            InterestArea.DIGITAL_MARKETING,
        ],
        skills=[("Excel", SkillRating.SOLO), ("SQL", SkillRating.WITH_HELP)],
    )
    pool = build_candidate_pool(intake)
    slugs = {s.career.slug for s in pool}
    assert "business-analyst-tech" in slugs or "digital-marketing-analyst" in slugs


def test_runner_agent1_validates() -> None:
    intake = _intake()
    result = run_agent(
        AgentName.CAREER_PATH_PICKER,
        {"intake": intake.model_dump(mode="json"), "exclude_slugs": []},
    )
    parsed = CareerPathPickerOutput.model_validate(result.output)
    assert {t.type.value for t in parsed.tracks} == {"Stretch", "Realistic", "Safe"}
