"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_certification_advisor.py -q"""

from app.agents.certification_advisor import (
    JD_FREQUENCY_THRESHOLD_PCT,
    advise_certifications,
    build_cert_frequency_map,
)
from app.agents.runner import run_agent
from app.agents.config import AgentName
from app.schemas.intake import BudgetInr, SkillRating
from app.services import data_registry
from tests.test_learning_path_generator import _intake


def test_data_analyst_cert_frequencies() -> None:
    cache = data_registry.load_jd_cache("data-analyst")
    freq = build_cert_frequency_map(cache)

    assert freq["Google Data Analytics Professional Certificate"] >= JD_FREQUENCY_THRESHOLD_PCT
    assert freq["Microsoft Power BI Data Analyst"] >= JD_FREQUENCY_THRESHOLD_PCT
    assert freq["IBM Data Analyst Professional Certificate"] == 30.0


def test_recommends_free_and_skips_paid_on_low_budget() -> None:
    intake = _intake(budget=BudgetInr.LOW)
    output = advise_certifications(intake, "data-analyst")

    assert len(output.recommended) >= 2
    assert "Google Data Analytics Professional Certificate" in {c.name for c in output.recommended}
    assert any(
        s["name"] == "Microsoft Power BI Data Analyst"
        for s in output.skip
    ), "Paid cert should land on skip list when budget is low"


def test_includes_optional_paid_on_mid_budget() -> None:
    intake = _intake(budget=BudgetInr.MID)
    output = advise_certifications(intake, "data-analyst")

    names = [c.name for c in output.recommended]
    assert "Google Data Analytics Professional Certificate" in names
    assert "Microsoft Power BI Data Analyst" in names
    paid = [c for c in output.recommended if "exam" in c.cost.lower()]
    assert len(paid) <= 1


def test_skip_list_has_do_not_buy_entries() -> None:
    output = advise_certifications(_intake(), "data-analyst")
    skip_names = {s["name"] for s in output.skip}
    assert any("bootcamp" in n.lower() for n in skip_names)
    assert any("udemy" in n.lower() for n in skip_names)


def test_runner_certification_advisor() -> None:
    intake = _intake(
        budget=BudgetInr.MID,
        skills=[("SQL", SkillRating.WITH_HELP)],
    )
    result = run_agent(
        AgentName.CERTIFICATION_ADVISOR,
        {
            "intake": intake.model_dump(mode="json"),
            "career_slug": "data-analyst",
            "role_name": "Data Analyst",
        },
    )
    assert result.agent_name == AgentName.CERTIFICATION_ADVISOR.value
    assert len(result.output["recommended"]) >= 2
    assert len(result.output["skip"]) >= 2
