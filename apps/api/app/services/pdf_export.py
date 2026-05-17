"""
Mission plan PDF export — structured summary of all agent outputs.
"""

from __future__ import annotations

import re
from typing import Any

from fpdf import FPDF

from app.schemas.agents import AgentOutputs, CareerTrack, TrackType
from app.services.plan_repository import parse_agent_outputs

_UNICODE_REPLACEMENTS = {
    "₹": "Rs.",
    "–": "-",
    "—": "-",
    "≥": ">=",
    "·": " - ",
    "’": "'",
    "“": '"',
    "”": '"',
}


def _safe(text: str | None, *, max_len: int | None = None) -> str:
    if not text:
        return ""
    out = str(text)
    for src, dst in _UNICODE_REPLACEMENTS.items():
        out = out.replace(src, dst)
    out = out.encode("latin-1", errors="replace").decode("latin-1")
    if max_len and len(out) > max_len:
        return out[: max_len - 1] + "..."
    return out


def _chosen_track(outputs: AgentOutputs, track_type: str | None) -> CareerTrack | None:
    if not track_type or not outputs.ai_reality_check:
        return None
    try:
        tt = TrackType(track_type)
    except ValueError:
        return None
    for track in outputs.ai_reality_check.tracks:
        if track.type == tt:
            return track
    return None


class MissionPlanPdf(FPDF):
    def _width(self) -> float:
        return self.epw

    def _reset_x(self) -> None:
        self.set_x(self.l_margin)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str) -> None:
        self._reset_x()
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(40, 40, 40)
        self.multi_cell(self._width(), 7, _safe(title))
        self.ln(1)

    def subsection(self, title: str) -> None:
        self._reset_x()
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(self._width(), 5, _safe(title))
        self.ln(0.5)

    def paragraph(self, text: str) -> None:
        self._reset_x()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(self._width(), 4.5, _safe(text))
        self.ln(1)

    def bullet(self, text: str) -> None:
        self._reset_x()
        self.set_font("Helvetica", "", 9)
        self.multi_cell(self._width(), 4.5, _safe(f"  - {text}"))


def build_plan_pdf(
    *,
    chosen_track_type: str | None,
    agent_outputs: AgentOutputs | dict[str, Any],
) -> bytes:
    outputs = (
        agent_outputs
        if isinstance(agent_outputs, AgentOutputs)
        else parse_agent_outputs(agent_outputs)
    )
    track = _chosen_track(outputs, chosen_track_type)
    role_title = track.name if track else (outputs.skill_gap.role if outputs.skill_gap else "Career Roadmap")

    pdf = MissionPlanPdf()
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(pdf.epw, 9, _safe(role_title))
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    line1 = f"{chosen_track_type or 'Mission'} track"
    pdf.cell(0, 5, _safe(line1), ln=True)
    if track:
        line2 = (
            f"{track.avg_starting_salary_band} - "
            f"~{track.time_to_job_estimate_months} months to first offer"
        )
        pdf.cell(0, 5, _safe(line2), ln=True)
    pdf.ln(2)

    if track:
        pdf.section_title("Chosen track")
        pdf.paragraph(track.why_recommended)
        if track.honest_warning:
            pdf.subsection("Honest warning")
            pdf.paragraph(track.honest_warning)
        if track.top_hiring_companies:
            pdf.bullet(f"Top hirers: {', '.join(track.top_hiring_companies[:6])}")
        if track.ai_risk_label:
            pdf.bullet(f"AI risk: Tier {track.ai_risk_tier} - {track.ai_risk_label}")

    briefing = outputs.ai_reality_check.disruption_briefing if outputs.ai_reality_check else None
    if briefing:
        pdf.section_title("AI disruption briefing")
        pdf.paragraph(briefing.summary)
        for path in briefing.rejected_paths[:5]:
            pdf.bullet(f"Rejected path: {path}")
        for callout in briefing.do_not_pursue_callouts[:4]:
            pdf.bullet(callout)

    if outputs.skill_gap and outputs.skill_gap.skills:
        pdf.section_title("Skill gaps")
        pdf.set_font("Helvetica", "B", 8)
        col_w = [42, 18, 18, 22, 18, 22]
        headers = ["Skill", "Now", "Need", "JD %", "Weeks", "Priority"]
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 6, h, border=1)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for skill in outputs.skill_gap.skills[:15]:
            row = [
                _safe(skill.name, max_len=28),
                str(skill.current_level),
                str(skill.required_level),
                f"{skill.demand_frequency_pct:.0f}",
                str(skill.weeks_to_bridge),
                skill.priority,
            ]
            for i, val in enumerate(row):
                pdf.cell(col_w[i], 5, val, border=1)
            pdf.ln()
        pdf._reset_x()
        pdf.ln(2)

    if outputs.learning_path and outputs.learning_path.weeks:
        pdf.section_title(
            f"Weekly learning plan ({outputs.learning_path.total_weeks} weeks)",
        )
        for week in outputs.learning_path.weeks:
            pdf.subsection(f"Week {week.week}: {week.focus_skill} ({week.hours}h)")
            for resource in week.resources[:3]:
                pdf.bullet(_safe(resource, max_len=90))
            pdf.paragraph(_safe(week.mini_task, max_len=200))
            if week.checkpoint:
                pdf.bullet("Checkpoint week")

    if outputs.projects and outputs.projects.projects:
        pdf.section_title("Portfolio projects")
        for project in outputs.projects.projects:
            pdf.subsection(f"{project.name} ({project.difficulty}, ~{project.hours_estimate}h)")
            pdf.paragraph(project.problem_statement)
            pdf.bullet(f"Stack: {', '.join(project.tech_stack)}")
            pdf.bullet(f"Output: {project.expected_output}")
            pdf.paragraph(f"Resume: {project.resume_bullet}")

    if outputs.certifications:
        if outputs.certifications.recommended:
            pdf.section_title("Recommended certifications")
            for cert in outputs.certifications.recommended:
                pdf.subsection(cert.name)
                pdf.paragraph(f"{cert.provider} | {cert.cost} | ~{cert.hours}h")
                pdf.paragraph(cert.why)
        if outputs.certifications.skip:
            pdf.section_title("Do not buy")
            for item in outputs.certifications.skip[:6]:
                pdf.subsection(item.get("name", "Item"))
                pdf.paragraph(item.get("why_skip", ""))

    if outputs.portfolio:
        pdf.section_title("Portfolio & outreach")
        pdf.subsection("Hosting")
        pdf.paragraph(re.sub(r"\*\*", "", outputs.portfolio.hosting_suggestion))
        if outputs.portfolio.connection_request_templates:
            pdf.subsection("Connection request templates")
            for i, template in enumerate(outputs.portfolio.connection_request_templates, 1):
                pdf.paragraph(f"{i}. {template}")
        if outputs.portfolio.linkedin_calendar:
            pdf.subsection("LinkedIn calendar")
            pdf.paragraph(
                f"{len(outputs.portfolio.linkedin_calendar)} posts across 12 weeks "
                "(learning, project, opinion, resource each week). "
                "Full templates available in your online mission plan.",
            )
        readme = outputs.portfolio.github_readme_md
        if readme:
            pdf.subsection("GitHub README (excerpt)")
            pdf.paragraph(_safe(readme, max_len=1200))

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.ln(4)
    pdf._reset_x()
    pdf.multi_cell(
        pdf.epw,
        4,
        _safe("Generated by Skill-to-Job Roadmap Builder. For the interactive plan, use your share link."),
    )

    out = pdf.output()
    return bytes(out)


def pdf_filename(plan_id: str, role_name: str | None = None) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (role_name or "mission-plan")).strip("-").lower()
    short_id = plan_id.replace("-", "")[:8] if plan_id != "demo" else "demo"
    return f"{slug or 'mission-plan'}-{short_id}.pdf"
