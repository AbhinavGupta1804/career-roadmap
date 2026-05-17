"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_ai_reality_check.py -q"""

from app.agents.ai_reality_check import (
    apply_reality_check,
    assert_plan_safe,
    patch_track,
    tracks_requiring_repick,
)
from app.agents.career_path_picker import build_tracks
from app.agents.runner import run_agent
from app.agents.config import AgentName
from app.schemas.agents import (
    AiRealityCheckOutput,
    AiRiskTier,
    CareerPathPickerOutput,
    CareerTrack,
    TrackType,
)
from tests.test_career_path_picker import _intake


def test_apply_tags_all_tracks_below_tier_4() -> None:
    intake = _intake()
    picker = build_tracks(intake)
    result = apply_reality_check(picker, intake)

    assert len(result.tracks) == 3
    for track in result.tracks:
        assert track.ai_risk_tier is not None
        assert track.ai_risk_tier.value <= 3
        assert track.ai_risk_label
        assert track.replaces
        assert track.amplifies
        assert track.evolved_role_2029
        assert track.survival_skills

    assert_plan_safe(result)


def test_disruption_briefing_always_present() -> None:
    intake = _intake()
    picker = build_tracks(intake)
    result = apply_reality_check(picker, intake)

    b = result.disruption_briefing
    assert b.summary.strip()
    assert len(b.do_not_pursue_callouts) >= 1


def test_tracks_requiring_repick_detects_tier_4_and_5() -> None:
    """Seed taxonomy has no tier 4/5 careers; verify detection logic on synthetic tags."""
    base = CareerTrack(
        name="Test Role",
        career_slug="data-analyst",
        type=TrackType.REALISTIC,
        why_recommended="test",
        avg_starting_salary_band="₹3–6 LPA",
        time_to_job_estimate_months=6,
        competition_level="medium",
        ai_risk_tier=AiRiskTier.SUNSET,
    )
    assert tracks_requiring_repick([base])
    base2 = base.model_copy(update={"ai_risk_tier": AiRiskTier.TAILWIND})
    assert not tracks_requiring_repick([base2])


def test_assert_plan_safe_rejects_tier_5() -> None:
    import pytest

    intake = _intake()
    picker = build_tracks(intake)
    output = apply_reality_check(picker, intake)
    tampered = output.model_copy(
        update={
            "tracks": [
                output.tracks[0].model_copy(update={"ai_risk_tier": AiRiskTier.SUNSET}),
                output.tracks[1],
                output.tracks[2],
            ]
        }
    )
    with pytest.raises(ValueError, match="tier 4/5"):
        assert_plan_safe(tampered)


def test_orchestrator_agent2_via_runner() -> None:
    intake = _intake()
    picker = run_agent(
        AgentName.CAREER_PATH_PICKER,
        {"intake": intake.model_dump(mode="json"), "exclude_slugs": []},
    )
    reality = run_agent(
        AgentName.AI_REALITY_CHECK,
        {
            "intake": intake.model_dump(mode="json"),
            "picker_output": picker.output,
        },
    )
    parsed = AiRealityCheckOutput.model_validate(reality.output)
    assert_plan_safe(parsed)


def test_build_tracks_never_produces_tier_4_or_5() -> None:
    for _ in range(5):
        intake = _intake()
        picker = build_tracks(intake)
        out = apply_reality_check(picker, intake)
        assert_plan_safe(out)


