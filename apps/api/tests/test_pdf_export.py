"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_pdf_export.py -q"""

from app.schemas.agents import TrackType
from app.services.pdf_export import build_plan_pdf, pdf_filename
from tests.test_portfolio_builder import _full_context


def _sample_outputs_dict() -> dict:
    intake, gaps, projects, learning, certs = _full_context()
    return {
        "chosen_track_type": TrackType.REALISTIC.value,
        "skill_gap": gaps.model_dump(mode="json"),
        "learning_path": learning.model_dump(mode="json"),
        "projects": projects.model_dump(mode="json"),
        "certifications": certs.model_dump(mode="json"),
        "ai_reality_check": {
            "tracks": [
                {
                    "name": "Analytics Engineer",
                    "career_slug": "analytics-engineer",
                    "type": TrackType.STRETCH.value,
                    "why_recommended": "Stretch if you add dbt.",
                    "avg_starting_salary_band": "Rs.8-14 LPA",
                    "time_to_job_estimate_months": 8,
                    "competition_level": "high",
                    "top_hiring_companies": ["Razorpay"],
                },
                {
                    "name": "Data Analyst",
                    "career_slug": "data-analyst",
                    "type": TrackType.REALISTIC.value,
                    "why_recommended": "Strong SQL + analytics fit.",
                    "avg_starting_salary_band": "Rs.6-12 LPA",
                    "time_to_job_estimate_months": 6,
                    "competition_level": "medium",
                    "top_hiring_companies": ["Razorpay", "Swiggy"],
                },
                {
                    "name": "Business Analyst",
                    "career_slug": "business-analyst-tech",
                    "type": TrackType.SAFE.value,
                    "why_recommended": "Lower technical bar.",
                    "avg_starting_salary_band": "Rs.5-10 LPA",
                    "time_to_job_estimate_months": 5,
                    "competition_level": "medium",
                    "top_hiring_companies": ["Zoho"],
                },
            ],
            "disruption_briefing": {
                "summary": "Analytics roles are augmented, not replaced.",
                "rejected_paths": [],
                "do_not_pursue_callouts": [],
            },
        },
    }


def test_build_plan_pdf_produces_valid_pdf() -> None:
    pdf = build_plan_pdf(
        chosen_track_type=TrackType.REALISTIC.value,
        agent_outputs=_sample_outputs_dict(),
    )
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 2000
    assert pdf.rstrip().endswith(b"%%EOF")


def test_pdf_filename_slug() -> None:
    name = pdf_filename("abc-123-def", "Data Analyst")
    assert name.endswith(".pdf")
    assert "data-analyst" in name
