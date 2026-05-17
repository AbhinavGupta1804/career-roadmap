from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.config import AgentName
from app.agents.exceptions import AgentError
from app.agents.runner import run_agent
from app.schemas.intake import IntakeForm

router = APIRouter(prefix="/agents", tags=["agents"])


class MockAgentTestRequest(BaseModel):
    agent_name: AgentName = AgentName.CAREER_PATH_PICKER
    intake: IntakeForm | None = None


class AgentRunLogResponse(BaseModel):
    agent_name: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_inr: float
    latency_ms: int
    mock: bool
    output: dict


@router.post("/test-mock", response_model=AgentRunLogResponse)
def test_mock_agent(body: MockAgentTestRequest | None = None) -> AgentRunLogResponse:
    """
    Step 4 acceptance: run one mock agent and return validated JSON + cost log.
    """
    body = body or MockAgentTestRequest()
    intake = body.intake or _sample_intake()

    try:
        if body.agent_name == AgentName.CAREER_PATH_PICKER:
            agent_input = {
                "intake": intake.model_dump(mode="json"),
                "careers": [],
                "exclude_slugs": [],
            }
        elif body.agent_name == AgentName.AI_REALITY_CHECK:
            picker = run_agent(
                AgentName.CAREER_PATH_PICKER,
                {
                    "intake": intake.model_dump(mode="json"),
                    "careers": [],
                    "exclude_slugs": [],
                },
            )
            agent_input = {
                "intake": intake.model_dump(mode="json"),
                "picker_output": picker.output,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Test endpoint supports picker or reality check; got {body.agent_name}",
            )

        result = run_agent(body.agent_name, agent_input)
        return AgentRunLogResponse(
            agent_name=result.agent_name,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_inr=result.cost_inr,
            latency_ms=result.latency_ms,
            mock=result.mock,
            output=result.output,
        )
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=exc.user_message) from exc


def _sample_intake() -> IntakeForm:
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
    )

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
            interest_bias=[InterestArea.MACHINE_LEARNING, InterestArea.DATA_SCIENCE],
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
