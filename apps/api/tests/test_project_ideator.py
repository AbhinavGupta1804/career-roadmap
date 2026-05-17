"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_project_ideator.py -q"""

from app.agents.project_ideator import (
    BANNED_PROJECT_PATTERNS,
    DIFFICULTY_ORDER,
    generate_projects,
    load_themes,
    projects_reference_jd_themes,
)
from app.agents.skill_gap_analyzer import analyze_skill_gaps
from app.agents.runner import run_agent
from app.agents.config import AgentName
from app.services import data_registry
from tests.test_learning_path_generator import _intake
from app.schemas.intake import SkillRating


def test_data_analyst_projects_reference_jd_themes() -> None:
    themes = load_themes("data-analyst", "Data Analyst")
    assert "SQL" in themes.top_skills
    assert "Power BI" in themes.top_skills
    assert themes.companies

    intake = _intake(
        skills=[
            ("SQL", SkillRating.WITH_HELP),
            ("Python", SkillRating.SOLO),
        ],
    )
    gaps = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")
    output = generate_projects("data-analyst", "Data Analyst", skill_gap=gaps)

    assert len(output.projects) == 5
    assert [p.difficulty for p in output.projects] == DIFFICULTY_ORDER
    assert projects_reference_jd_themes(themes, output.projects)

    combined = " ".join(
        p.problem_statement + p.name + p.resume_bullet for p in output.projects
    ).lower()
    assert "cross-functional" in combined or "jd" in combined
    assert any(c.lower() in combined for c in themes.companies[:2])
    assert "sql" in combined
    assert "power bi" in combined or "excel" in combined


def test_no_todo_or_calculator_projects() -> None:
    output = generate_projects("backend-developer", "Backend Developer")
    for project in output.projects:
        assert not BANNED_PROJECT_PATTERNS.search(
            f"{project.name} {project.problem_statement}",
        )


def test_projects_have_required_fields() -> None:
    output = generate_projects("data-analyst", "Data Analyst")
    hours = [12, 20, 30, 40, 60]
    for project, expected_hours in zip(output.projects, hours, strict=True):
        assert project.problem_statement
        assert project.dataset_or_api
        assert project.expected_output
        assert project.hours_estimate == expected_hours
        assert len(project.tech_stack) >= 1
        assert project.resume_bullet
        assert len(project.resume_bullet) > 20


def test_runner_agent5_with_skill_gap() -> None:
    intake = _intake()
    gaps = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")
    result = run_agent(
        AgentName.PROJECT_IDEATOR,
        {
            "intake": intake.model_dump(mode="json"),
            "career_slug": "data-analyst",
            "role_name": "Data Analyst",
            "skill_gap": gaps.model_dump(mode="json"),
        },
    )
    assert result.mock is True
    assert len(result.output["projects"]) == 5
    themes = load_themes("data-analyst", "Data Analyst")
    from app.schemas.agents import PortfolioProject

    projects = [PortfolioProject.model_validate(p) for p in result.output["projects"]]
    assert projects_reference_jd_themes(themes, projects)


def test_jd_corpus_skills_match_data_analyst_cache() -> None:
    cache = data_registry.load_jd_cache("data-analyst")
    themes = load_themes("data-analyst", "Data Analyst")
    assert themes.jd_count == len(cache.jds) == 50
    for skill in ["SQL", "Python", "Excel", "Power BI", "Tableau", "Statistics"]:
        assert skill in themes.top_skills
