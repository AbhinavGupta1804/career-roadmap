"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_portfolio_builder.py -q"""

from app.agents.certification_advisor import advise_certifications
from app.agents.learning_path_generator import generate_learning_path
from app.agents.portfolio_builder import (
    LINKEDIN_WEEKS,
    POSTS_PER_WEEK,
    build_portfolio,
    suggest_hosting,
)
from app.agents.project_ideator import generate_projects
from app.agents.runner import run_agent
from app.agents.skill_gap_analyzer import analyze_skill_gaps
from app.agents.config import AgentName
from app.schemas.intake import SkillRating
from tests.test_learning_path_generator import _intake


def _full_context():
    intake = _intake(
        skills=[
            ("SQL", SkillRating.WITH_HELP),
            ("Python", SkillRating.SOLO),
            ("Excel", SkillRating.SOLO),
        ],
    )
    gaps = analyze_skill_gaps(intake, "data-analyst", "Data Analyst")
    projects = generate_projects("data-analyst", "Data Analyst", skill_gap=gaps)
    learning = generate_learning_path(intake, "data-analyst", skill_gap=gaps)
    certs = advise_certifications(intake, "data-analyst")
    return intake, gaps, projects, learning, certs


def test_github_readme_projects_only() -> None:
    intake, gaps, projects, learning, certs = _full_context()
    output = build_portfolio(
        intake,
        "data-analyst",
        "Data Analyst",
        projects=projects,
        learning_path=learning,
        skill_gap=gaps,
        certifications=certs,
    )
    for project in projects.projects:
        assert project.name in output.github_readme_md
    assert "student building toward" not in output.github_readme_md
    assert "Aspiring" not in output.github_readme_md


def test_portfolio_site_has_five_sections() -> None:
    intake, gaps, projects, learning, _ = _full_context()
    output = build_portfolio(
        intake,
        "data-analyst",
        "Data Analyst",
        projects=projects,
        learning_path=learning,
        skill_gap=gaps,
    )
    sections = [s.section for s in output.portfolio_site_sections]
    assert sections == ["hero", "about", "projects", "skills", "contact"]
    assert projects.projects[0].name in next(
        s.content for s in output.portfolio_site_sections if s.section == "projects"
    )


def test_linkedin_calendar_twelve_weeks_four_posts_each() -> None:
    intake, gaps, projects, learning, certs = _full_context()
    output = build_portfolio(
        intake,
        "data-analyst",
        "Data Analyst",
        projects=projects,
        learning_path=learning,
        skill_gap=gaps,
        certifications=certs,
    )
    assert len(output.linkedin_calendar) == LINKEDIN_WEEKS * POSTS_PER_WEEK
    weeks = {p.week for p in output.linkedin_calendar}
    assert weeks == set(range(1, LINKEDIN_WEEKS + 1))
    for week in range(1, LINKEDIN_WEEKS + 1):
        week_posts = [p for p in output.linkedin_calendar if p.week == week]
        assert len(week_posts) == POSTS_PER_WEEK
        types = {p.post_type for p in week_posts}
        assert types == {"learning", "project", "opinion", "resource"}


def test_connection_templates_count_five() -> None:
    intake, _, projects, learning, _ = _full_context()
    output = build_portfolio(
        intake,
        "data-analyst",
        "Data Analyst",
        projects=projects,
        learning_path=learning,
        top_hiring_companies=["Razorpay", "Swiggy"],
    )
    assert len(output.connection_request_templates) == 5
    assert any("Razorpay" in t or "Swiggy" in t for t in output.connection_request_templates)


def test_hosting_suggestion_for_react_stack() -> None:
    intake, gaps, projects, _, _ = _full_context()
    react_projects = projects.model_copy(deep=True)
    react_projects.projects[0].tech_stack = ["React", "TypeScript", "Node.js"]
    hint = suggest_hosting(react_projects.projects, "full-stack-developer")
    assert "Vercel" in hint


def test_runner_portfolio_builder() -> None:
    intake, gaps, projects, learning, certs = _full_context()
    result = run_agent(
        AgentName.PORTFOLIO_BUILDER,
        {
            "intake": intake.model_dump(mode="json"),
            "career_slug": "data-analyst",
            "role_name": "Data Analyst",
            "skill_gap": gaps.model_dump(mode="json"),
            "projects": projects.model_dump(mode="json"),
            "learning_path": learning.model_dump(mode="json"),
            "certifications": certs.model_dump(mode="json"),
            "top_hiring_companies": ["Razorpay"],
        },
    )
    assert result.agent_name == AgentName.PORTFOLIO_BUILDER.value
    assert len(result.output["linkedin_calendar"]) == 48
    assert len(result.output["connection_request_templates"]) == 5
