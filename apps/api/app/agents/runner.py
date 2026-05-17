from __future__ import annotations

import json
import re
import time
from typing import Any, TypeVar

from pydantic import BaseModel

from app.agents.config import AGENT_SPECS, AgentModel, AgentName
from app.agents.cost import tokens_to_cost_inr
from app.agents.exceptions import AgentError
from app.agents.prompts import SYSTEM_PROMPTS
from app.config import get_settings

T = TypeVar("T", bound=BaseModel)


class AgentRunResult(BaseModel):
    agent_name: str
    output: dict[str, Any]
    parsed: BaseModel
    input_tokens: int
    output_tokens: int
    cost_inr: float
    latency_ms: int
    model: str
    mock: bool


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise


def _run_mock(agent_name: AgentName, agent_input: dict[str, Any]) -> AgentRunResult:
    from app.agents import mock_outputs
    from app.schemas.intake import IntakeForm

    start = time.perf_counter()
    spec = AGENT_SPECS[agent_name]
    intake = IntakeForm.model_validate(agent_input["intake"])

    if agent_name == AgentName.CAREER_PATH_PICKER:
        from app.agents.career_path_picker import build_tracks

        parsed = build_tracks(
            intake,
            exclude_slugs=set(agent_input.get("exclude_slugs", [])),
        )
    elif agent_name == AgentName.AI_REALITY_CHECK:
        from app.agents.ai_reality_check import apply_reality_check
        from app.schemas.agents import CareerPathPickerOutput

        picker = CareerPathPickerOutput.model_validate(agent_input["picker_output"])
        parsed = apply_reality_check(picker, intake)
    elif agent_name == AgentName.SKILL_GAP_ANALYZER:
        from app.agents.skill_gap_analyzer import analyze_skill_gaps

        parsed = analyze_skill_gaps(
            intake,
            agent_input["career_slug"],
            agent_input["role_name"],
        )
    elif agent_name == AgentName.LEARNING_PATH_GENERATOR:
        from app.agents.learning_path_generator import (
            generate_learning_path,
            parse_skill_gap_from_input,
        )

        parsed = generate_learning_path(
            intake,
            agent_input["career_slug"],
            skill_gap=parse_skill_gap_from_input(agent_input),
            role_name=agent_input.get("role_name"),
        )
    elif agent_name == AgentName.PROJECT_IDEATOR:
        from app.agents.project_ideator import (
            generate_projects,
            parse_skill_gap_from_input,
        )

        parsed = generate_projects(
            agent_input["career_slug"],
            agent_input["role_name"],
            skill_gap=parse_skill_gap_from_input(agent_input),
        )
    elif agent_name == AgentName.CERTIFICATION_ADVISOR:
        from app.agents.certification_advisor import advise_certifications

        parsed = advise_certifications(
            intake,
            agent_input["career_slug"],
        )
    elif agent_name == AgentName.PORTFOLIO_BUILDER:
        from app.agents.portfolio_builder import (
            build_portfolio,
            parse_certifications_from_input,
            parse_learning_path_from_input,
            parse_projects_from_input,
            parse_skill_gap_from_input,
        )

        parsed = build_portfolio(
            intake,
            agent_input["career_slug"],
            agent_input["role_name"],
            projects=parse_projects_from_input(agent_input),
            learning_path=parse_learning_path_from_input(agent_input),
            skill_gap=parse_skill_gap_from_input(agent_input),
            certifications=parse_certifications_from_input(agent_input),
            top_hiring_companies=agent_input.get("top_hiring_companies"),
        )
    else:
        raise AgentError(agent_name.value, f"No mock for {agent_name}")

    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=agent_name.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=0,
        output_tokens=0,
        cost_inr=0.0,
        latency_ms=latency_ms,
        model="mock",
        mock=True,
    )


def _run_career_path_picker_llm(
    agent_input: dict[str, Any],
    model: AgentModel,
) -> AgentRunResult:
    """Agent 1: deterministic picks, then LLM enriches narrative fields."""
    from app.schemas.intake import IntakeForm
    from app.agents.career_path_picker import build_tracks, enrich_tracks_with_llm

    settings = get_settings()
    intake = IntakeForm.model_validate(agent_input["intake"])
    exclude = set(agent_input.get("exclude_slugs", []))

    start = time.perf_counter()
    base = build_tracks(intake, exclude)

    if not settings.anthropic_api_key:
        parsed = base
        mock = True
        input_tokens = output_tokens = 0
        cost_inr = 0.0
        model_name = "scoring-only"
    else:
        parsed, input_tokens, output_tokens = enrich_tracks_with_llm(
            base,
            intake,
            api_key=settings.anthropic_api_key,
            model=model.value,
        )
        mock = False
        cost_inr = tokens_to_cost_inr(
            model, input_tokens, output_tokens, settings.usd_to_inr
        )
        model_name = model.value

    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.CAREER_PATH_PICKER.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_inr=cost_inr,
        latency_ms=latency_ms,
        model=model_name,
        mock=mock,
    )


def _run_ai_reality_check_llm(
    agent_input: dict[str, Any],
    model: AgentModel,
) -> AgentRunResult:
    from app.agents.ai_reality_check import apply_reality_check, enrich_with_llm
    from app.schemas.agents import CareerPathPickerOutput
    from app.schemas.intake import IntakeForm

    settings = get_settings()
    intake = IntakeForm.model_validate(agent_input["intake"])
    picker = CareerPathPickerOutput.model_validate(agent_input["picker_output"])

    start = time.perf_counter()
    base = apply_reality_check(picker, intake)

    if not settings.anthropic_api_key:
        parsed = base
        mock = True
        input_tokens = output_tokens = 0
        cost_inr = 0.0
        model_name = "taxonomy-only"
    else:
        parsed, input_tokens, output_tokens = enrich_with_llm(
            base,
            intake,
            api_key=settings.anthropic_api_key,
            model=model.value,
        )
        mock = False
        cost_inr = tokens_to_cost_inr(
            model, input_tokens, output_tokens, settings.usd_to_inr
        )
        model_name = model.value

    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.AI_REALITY_CHECK.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_inr=cost_inr,
        latency_ms=latency_ms,
        model=model_name,
        mock=mock,
    )


def _run_portfolio_builder(agent_input: dict[str, Any]) -> AgentRunResult:
    """Agent 7: README, site sections, hosting, LinkedIn calendar, outreach."""
    from app.agents.portfolio_builder import (
        build_portfolio,
        parse_certifications_from_input,
        parse_learning_path_from_input,
        parse_projects_from_input,
        parse_skill_gap_from_input,
    )
    from app.schemas.intake import IntakeForm

    intake = IntakeForm.model_validate(agent_input["intake"])
    start = time.perf_counter()
    parsed = build_portfolio(
        intake,
        agent_input["career_slug"],
        agent_input["role_name"],
        projects=parse_projects_from_input(agent_input),
        learning_path=parse_learning_path_from_input(agent_input),
        skill_gap=parse_skill_gap_from_input(agent_input),
        certifications=parse_certifications_from_input(agent_input),
        top_hiring_companies=agent_input.get("top_hiring_companies"),
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.PORTFOLIO_BUILDER.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=0,
        output_tokens=0,
        cost_inr=0.0,
        latency_ms=latency_ms,
        model="template-engine",
        mock=True,
    )


def _run_certification_advisor(agent_input: dict[str, Any]) -> AgentRunResult:
    """Agent 6: JD corpus cert frequency + budget-aware recommendations."""
    from app.agents.certification_advisor import advise_certifications
    from app.schemas.intake import IntakeForm

    intake = IntakeForm.model_validate(agent_input["intake"])
    start = time.perf_counter()
    parsed = advise_certifications(intake, agent_input["career_slug"])
    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.CERTIFICATION_ADVISOR.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=0,
        output_tokens=0,
        cost_inr=0.0,
        latency_ms=latency_ms,
        model="jd-corpus",
        mock=True,
    )


def _run_project_ideator(agent_input: dict[str, Any]) -> AgentRunResult:
    """Agent 5: deterministic JD-themed portfolio projects."""
    from app.agents.project_ideator import (
        generate_projects,
        parse_skill_gap_from_input,
    )
    from app.schemas.intake import IntakeForm

    IntakeForm.model_validate(agent_input["intake"])
    start = time.perf_counter()
    parsed = generate_projects(
        agent_input["career_slug"],
        agent_input["role_name"],
        skill_gap=parse_skill_gap_from_input(agent_input),
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.PROJECT_IDEATOR.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=0,
        output_tokens=0,
        cost_inr=0.0,
        latency_ms=latency_ms,
        model="jd-themes",
        mock=True,
    )


def _run_learning_path_generator(agent_input: dict[str, Any]) -> AgentRunResult:
    """Agent 4: deterministic plan from ordered gaps + resource library."""
    from app.agents.learning_path_generator import (
        generate_learning_path,
        parse_skill_gap_from_input,
    )
    from app.schemas.data_models import LearningResource
    from app.schemas.intake import IntakeForm

    intake = IntakeForm.model_validate(agent_input["intake"])
    raw_resources = agent_input.get("resources") or []
    resources = (
        [LearningResource.model_validate(r) for r in raw_resources]
        if raw_resources
        else None
    )

    start = time.perf_counter()
    parsed = generate_learning_path(
        intake,
        agent_input["career_slug"],
        skill_gap=parse_skill_gap_from_input(agent_input),
        resources=resources,
        role_name=agent_input.get("role_name"),
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.LEARNING_PATH_GENERATOR.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=0,
        output_tokens=0,
        cost_inr=0.0,
        latency_ms=latency_ms,
        model="schedule-engine",
        mock=True,
    )


def _run_skill_gap_analyzer_llm(
    agent_input: dict[str, Any],
    model: AgentModel,
) -> AgentRunResult:
    """Agent 3: Haiku JD skill extraction → frequency map → gap matrix."""
    from app.agents.skill_gap_analyzer import (
        analyze_skill_gaps,
        extract_skills_with_haiku,
    )
    from app.schemas.intake import IntakeForm
    from app.services import data_registry

    settings = get_settings()
    intake = IntakeForm.model_validate(agent_input["intake"])
    career_slug = agent_input["career_slug"]
    role_name = agent_input["role_name"]

    start = time.perf_counter()
    skills_per_jd = None
    input_tokens = output_tokens = 0
    model_name = "jd-corpus"

    try:
        cache = data_registry.load_jd_cache(career_slug)
    except FileNotFoundError:
        cache = None

    if cache and settings.anthropic_api_key:
        try:
            skills_per_jd, input_tokens, output_tokens = extract_skills_with_haiku(
                cache,
                api_key=settings.anthropic_api_key,
                model=model.value,
            )
            model_name = model.value
        except Exception:
            skills_per_jd = None

    parsed = analyze_skill_gaps(
        intake,
        career_slug,
        role_name,
        skills_per_jd=skills_per_jd,
    )

    cost_inr = (
        tokens_to_cost_inr(model, input_tokens, output_tokens, settings.usd_to_inr)
        if input_tokens or output_tokens
        else 0.0
    )
    mock = not bool(input_tokens or output_tokens)

    latency_ms = int((time.perf_counter() - start) * 1000)
    return AgentRunResult(
        agent_name=AgentName.SKILL_GAP_ANALYZER.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_inr=cost_inr,
        latency_ms=latency_ms,
        model=model_name if not mock else "jd-corpus",
        mock=mock,
    )


def _run_llm(
    agent_name: AgentName,
    agent_input: dict[str, Any],
    model: AgentModel,
) -> AgentRunResult:
    if agent_name == AgentName.CAREER_PATH_PICKER:
        return _run_career_path_picker_llm(agent_input, model)
    if agent_name == AgentName.AI_REALITY_CHECK:
        return _run_ai_reality_check_llm(agent_input, model)
    if agent_name == AgentName.SKILL_GAP_ANALYZER:
        return _run_skill_gap_analyzer_llm(agent_input, model)
    if agent_name == AgentName.LEARNING_PATH_GENERATOR:
        return _run_learning_path_generator(agent_input)
    if agent_name == AgentName.PROJECT_IDEATOR:
        return _run_project_ideator(agent_input)
    if agent_name == AgentName.CERTIFICATION_ADVISOR:
        return _run_certification_advisor(agent_input)
    if agent_name == AgentName.PORTFOLIO_BUILDER:
        return _run_portfolio_builder(agent_input)

    settings = get_settings()
    if not settings.anthropic_api_key:
        raise AgentError(
            agent_name.value,
            "ANTHROPIC_API_KEY not set",
            user_message="AI service is not configured. Enable mock mode or add an API key.",
        )

    try:
        import anthropic
    except ImportError as exc:
        raise AgentError(
            agent_name.value,
            "anthropic package not installed",
        ) from exc

    spec = AGENT_SPECS[agent_name]
    system = SYSTEM_PROMPTS[agent_name]
    user_content = json.dumps(agent_input, default=str)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    start = time.perf_counter()

    response = client.messages.create(
        model=model.value,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )

    latency_ms = int((time.perf_counter() - start) * 1000)
    text_blocks = [b.text for b in response.content if b.type == "text"]
    raw_text = "\n".join(text_blocks)
    payload = _extract_json(raw_text)
    parsed = spec.output_schema.model_validate(payload)

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost_inr = tokens_to_cost_inr(
        model, input_tokens, output_tokens, settings.usd_to_inr
    )

    return AgentRunResult(
        agent_name=agent_name.value,
        output=parsed.model_dump(mode="json"),
        parsed=parsed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_inr=cost_inr,
        latency_ms=latency_ms,
        model=model.value,
        mock=False,
    )


def run_agent(
    name: str | AgentName,
    agent_input: dict[str, Any],
    model: AgentModel | str | None = None,
) -> AgentRunResult:
    """
    Run one agent with optional retry. Uses mock mode when configured or no API key.
    """
    agent_name = AgentName(name) if isinstance(name, str) else name
    if agent_name not in AGENT_SPECS:
        raise AgentError(str(name), f"Unknown agent: {name}")

    settings = get_settings()
    spec = AGENT_SPECS[agent_name]
    chosen_model = (
        AgentModel(model)
        if isinstance(model, str) and model
        else model
        if isinstance(model, AgentModel)
        else spec.default_model
    )

    use_mock = settings.agent_mock_mode or not settings.anthropic_api_key
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            if use_mock:
                return _run_mock(agent_name, agent_input)
            return _run_llm(agent_name, agent_input, chosen_model)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == 0:
                continue
            break

    message = str(last_error) if last_error else "Unknown error"
    user_message = "We couldn't generate part of your plan. Please try again."
    if isinstance(last_error, ModuleNotFoundError) and "anthropic" in str(last_error):
        user_message = (
            "Anthropic SDK is not installed. Run: pip install -r requirements.txt"
        )
    elif "authentication_error" in message or "invalid x-api-key" in message:
        user_message = (
            "Anthropic API key is invalid or expired. Check ANTHROPIC_API_KEY in apps/api/.env"
        )
    raise AgentError(
        agent_name.value,
        message,
        user_message=user_message,
    ) from last_error
