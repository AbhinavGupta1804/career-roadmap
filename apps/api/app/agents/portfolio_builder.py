"""
Agent 7: Portfolio Builder — README, site copy, hosting, LinkedIn calendar, outreach.

Uses Agent 5 projects and Agent 4 learning plan. Deterministic templates personalized
from intake + track context.
"""

from __future__ import annotations

from typing import Any, Literal

from app.schemas.agents import (
    CertificationAdvisorOutput,
    LearningPathGeneratorOutput,
    LinkedInPost,
    PortfolioBuilderOutput,
    PortfolioProject,
    PortfolioSiteSection,
    ProjectIdeatorOutput,
    SkillGapAnalyzerOutput,
)
from app.schemas.intake import IntakeForm

LINKEDIN_WEEKS = 12
POSTS_PER_WEEK = 4
POST_TYPES: list[Literal["project", "learning", "opinion", "resource"]] = [
    "learning",
    "project",
    "opinion",
    "resource",
]

OPINION_HOOKS: dict[str, list[str]] = {
    "data-analyst": [
        "Dashboards don't get you hired — decisions do.",
        "SQL fluency beats another Python library for most DA fresher roles.",
        "Tier-2 grads win with narrative + metrics, not pedigree alone.",
    ],
    "backend-developer": [
        "CRUD tutorials won't pass system design screens — own one real API.",
        "Indian startups care about deployability, not LeetCode rank alone.",
    ],
    "frontend-developer": [
        "Pixel-perfect clones matter less than accessible, fast UX.",
        "Recruiters skim GitHub READMEs before they open your live demo.",
    ],
    "full-stack-developer": [
        "Full-stack means end-to-end ownership, not half-depth on both sides.",
    ],
    "devops-engineer": [
        "Runbooks and incident write-ups signal maturity better than cert walls.",
    ],
    "ml-engineer": [
        "ML hiring in India still starts with SQL + metrics, not notebooks alone.",
    ],
    "data-scientist": [
        "Business impact framing beats model accuracy slides for fresher DS.",
    ],
    "ui-ux-designer": [
        "Case studies beat Dribbble shots for Indian product design interviews.",
    ],
    "cybersecurity-analyst": [
        "Documented labs beat vague 'interested in cyber' bios every time.",
    ],
    "mobile-developer": [
        "Ship one polished app build — store listing optional for campus hiring.",
    ],
}

DEFAULT_OPINIONS = [
    "Consistency on LinkedIn beats viral posts for campus recruiters.",
    "Show work in public weekly — hiring managers notice streaks.",
    "Your college tier is a filter, not a sentence — proof beats pedigree.",
]


def parse_projects_from_input(agent_input: dict[str, Any]) -> ProjectIdeatorOutput | None:
    raw = agent_input.get("projects")
    if not raw:
        return None
    return ProjectIdeatorOutput.model_validate(raw)


def parse_learning_path_from_input(
    agent_input: dict[str, Any],
) -> LearningPathGeneratorOutput | None:
    raw = agent_input.get("learning_path")
    if not raw:
        return None
    return LearningPathGeneratorOutput.model_validate(raw)


def parse_skill_gap_from_input(agent_input: dict[str, Any]) -> SkillGapAnalyzerOutput | None:
    raw = agent_input.get("skill_gap")
    if not raw:
        return None
    return SkillGapAnalyzerOutput.model_validate(raw)


def parse_certifications_from_input(
    agent_input: dict[str, Any],
) -> CertificationAdvisorOutput | None:
    raw = agent_input.get("certifications")
    if not raw:
        return None
    return CertificationAdvisorOutput.model_validate(raw)


def _student_display_name(intake: IntakeForm) -> str:
    if intake.skills_and_goals.github_url:
        path = str(intake.skills_and_goals.github_url).rstrip("/").split("/")[-1]
        if path and path not in ("github.com", ""):
            return path.replace("-", " ").title()
    return f"{intake.profile.city} · {intake.profile.stream.value} Student"


def _collect_stack(projects: list[PortfolioProject]) -> set[str]:
    stack: set[str] = set()
    for project in projects:
        for tech in project.tech_stack:
            stack.add(tech.lower())
    return stack


def suggest_hosting(projects: list[PortfolioProject], career_slug: str) -> str:
    stack = _collect_stack(projects)
    if stack & {"react", "next.js", "nextjs", "node.js", "nodejs", "typescript"}:
        return (
            "**Vercel** (free hobby tier) — connect your GitHub repo for automatic "
            "deploys on every push. Ideal for React/Next portfolios with live demos."
        )
    if stack & {"vue", "nuxt"}:
        return (
            "**Netlify** or **Vercel** — both free for static/SSR Vue sites with "
            "custom domains via DNS."
        )
    if stack & {"android", "kotlin", "flutter"}:
        return (
            "**GitHub Pages** for project write-ups + link to APK/TestFlight or "
            "Play Store internal track when ready."
        )
    if stack & {"power bi", "tableau", "excel"}:
        return (
            "**GitHub Pages** for case-study markdown + embed **Power BI Public** "
            "or Tableau Public dashboards in your site."
        )
    if "figma" in stack or career_slug == "ui-ux-designer":
        return (
            "**Notion** or **Framer** free tier for case-study sites; export Figma "
            "frames as PNG and host assets on GitHub."
        )
    return (
        "**GitHub Pages** (free) — publish from `/docs` or `gh-pages` branch; "
        "pairs naturally with your project repos and README."
    )


def build_github_readme(
    intake: IntakeForm,
    role_name: str,
    projects: list[PortfolioProject],
    skill_gap: SkillGapAnalyzerOutput | None,
    certifications: CertificationAdvisorOutput | None,
) -> str:
    """GitHub profile README — portfolio projects only."""
    _ = (intake, role_name, skill_gap, certifications)
    if not projects:
        return "_Projects will appear here after your mission plan is generated._"

    sections: list[str] = []
    for i, project in enumerate(projects, start=1):
        stack = ", ".join(project.tech_stack)
        sections.append(
            f"### {i}. {project.name} ({project.difficulty})\n"
            f"{project.problem_statement}\n\n"
            f"- **Stack:** {stack}\n"
            f"- **Output:** {project.expected_output}\n"
            f"- **Data/API:** {project.dataset_or_api or 'N/A'}\n"
            f"- **Resume:** {project.resume_bullet}"
        )
    return "\n\n".join(sections)


def build_site_sections(
    intake: IntakeForm,
    role_name: str,
    projects: list[PortfolioProject],
    skill_gap: SkillGapAnalyzerOutput | None,
) -> list[PortfolioSiteSection]:
    name = _student_display_name(intake)
    companies = ", ".join(intake.skills_and_goals.dream_companies) or "growth-stage tech teams"

    hero = (
        f"Hi, I'm **{name}** — a {intake.profile.year_of_study.value}-year "
        f"{intake.profile.stream.value} student from **{intake.profile.city}** "
        f"targeting **{role_name}** roles ({intake.skills_and_goals.target_salary_band.value}). "
        f"I ship portfolio work {intake.profile.hours_per_day.value}/day and I'm open to "
        f"{intake.profile.relocation.value.lower()} roles."
    )

    about = (
        f"I'm focused on **{role_name}** because it matches my interests in "
        f"{', '.join(i.value for i in intake.self_assessment.interest_bias)}. "
        f"College: {intake.profile.college_tier.value} · CGPA band: {intake.profile.cgpa_band.value}. "
        f"Primary goal: **{intake.skills_and_goals.primary_goal.value}** within "
        f"**{intake.skills_and_goals.timeline_to_job.value}**.\n\n"
    )
    if intake.skills_and_goals.has_internship and intake.skills_and_goals.internship_brief:
        about += f"**Internship:** {intake.skills_and_goals.internship_brief}\n\n"
    if intake.skills_and_goals.projects_text:
        about += f"**Background:** {intake.skills_and_goals.projects_text}\n\n"
    about += f"Dream companies: **{companies}**."

    project_lines = []
    for project in projects:
        project_lines.append(
            f"**{project.name}** ({project.difficulty}, ~{project.hours_estimate}h)\n"
            f"{project.problem_statement}\n"
            f"Stack: {', '.join(project.tech_stack)} → {project.expected_output}"
        )
    projects_content = (
        "\n\n".join(project_lines)
        if project_lines
        else "Your five JD-aligned projects will appear here after the mission plan runs."
    )

    if skill_gap and skill_gap.skills:
        skill_lines = [
            f"**{s.name}** — {s.current_level}/5 → {s.required_level}/5 "
            f"({s.demand_frequency_pct:.0f}% of JDs, {s.priority})"
            for s in skill_gap.skills[:10]
        ]
        skills_content = "\n".join(skill_lines)
    else:
        skills_content = "Skill gap analysis will populate this section."

    contact = (
        f"📍 {intake.profile.city} · Open to {intake.profile.relocation.value}\n"
        f"🎯 {role_name} · {intake.skills_and_goals.primary_goal.value}\n"
        f"💼 Target band: {intake.skills_and_goals.target_salary_band.value}\n\n"
        "LinkedIn: [your-profile]\n"
        "GitHub: [your-username]\n"
        "Email: you@college.edu"
    )
    if intake.skills_and_goals.github_url:
        contact = contact.replace(
            "GitHub: [your-username]",
            f"GitHub: {intake.skills_and_goals.github_url}",
        )

    return [
        PortfolioSiteSection(section="hero", content=hero),
        PortfolioSiteSection(section="about", content=about),
        PortfolioSiteSection(section="projects", content=projects_content),
        PortfolioSiteSection(section="skills", content=skills_content),
        PortfolioSiteSection(section="contact", content=contact),
    ]


def _project_for_week(week: int, projects: list[PortfolioProject]) -> PortfolioProject | None:
    if not projects:
        return None
    # Spread 5 projects across 12 weeks (capstone in final third)
    idx = min((week - 1) * len(projects) // LINKEDIN_WEEKS, len(projects) - 1)
    return projects[idx]


def _learning_week(plan: LearningPathGeneratorOutput | None, week: int) -> tuple[str, list[str]]:
    if not plan or not plan.weeks:
        return "core skills", []
    idx = (week - 1) % len(plan.weeks)
    lw = plan.weeks[idx]
    return lw.focus_skill, lw.resources[:2]


def build_linkedin_calendar(
    role_name: str,
    career_slug: str,
    projects: list[PortfolioProject],
    learning_path: LearningPathGeneratorOutput | None,
    certifications: CertificationAdvisorOutput | None,
) -> list[LinkedInPost]:
    opinions = OPINION_HOOKS.get(career_slug, DEFAULT_OPINIONS)
    posts: list[LinkedInPost] = []

    for week in range(1, LINKEDIN_WEEKS + 1):
        focus, resources = _learning_week(learning_path, week)
        project = _project_for_week(week, projects)

        for slot, post_type in enumerate(POST_TYPES, start=1):
            if post_type == "learning":
                resource_hint = resources[0] if resources else "this week's mission plan resource"
                template = (
                    f"**Week {week} · Learning update**\n\n"
                    f"Focused on **{focus}** for my {role_name} journey.\n\n"
                    f"What I did:\n"
                    f"• Completed [specific exercise / module]\n"
                    f"• Practiced [skill] for ~[X] hours\n"
                    f"• Blocker: [one honest challenge]\n\n"
                    f"Resource I'm using: {resource_hint}\n\n"
                    f"#LearningInPublic #{career_slug.replace('-', '')} #CareerRoadmap"
                )
            elif post_type == "project":
                if project:
                    template = (
                        f"**Week {week} · Project showcase**\n\n"
                        f"Building **{project.name}** ({project.difficulty}).\n\n"
                        f"Problem: {project.problem_statement[:180]}{'…' if len(project.problem_statement) > 180 else ''}\n\n"
                        f"Stack: {', '.join(project.tech_stack[:4])}\n"
                        f"This week I shipped: [screenshot / PR link / demo GIF]\n\n"
                        f"#{project.difficulty} #Portfolio #{role_name.replace(' ', '')}"
                    )
                else:
                    template = (
                        f"**Week {week} · Project showcase**\n\n"
                        f"Shared progress on my {role_name} capstone — "
                        f"[link to repo or demo].\n\n"
                        f"#BuildInPublic #Portfolio"
                    )
            elif post_type == "opinion":
                hook = opinions[(week + slot) % len(opinions)]
                template = (
                    f"**Week {week} · Opinion**\n\n"
                    f"Hot take for {role_name} aspirants in India:\n\n"
                    f"\"{hook}\"\n\n"
                    f"My experience: [2–3 sentences with a concrete example]\n\n"
                    f"Agree or disagree? 👇\n\n"
                    f"#CareerAdvice #{career_slug.replace('-', '')}"
                )
            else:  # resource
                cert_name = (
                    certifications.recommended[0].name
                    if certifications and certifications.recommended
                    else None
                )
                extra = (
                    f"\nAlso pursuing: **{cert_name}** (audit)."
                    if cert_name and week % 4 == 0
                    else ""
                )
                template = (
                    f"**Week {week} · Resource share**\n\n"
                    f"Free resource that helped my **{focus}** prep:\n\n"
                    f"→ {resources[0] if resources else '[link + one-line why it helped]'}\n"
                    f"→ Best for: {role_name} freshers with limited budget{extra}\n\n"
                    f"Save this if you're on a similar path.\n\n"
                    f"#FreeResources #Upskilling"
                )

            posts.append(LinkedInPost(week=week, post_type=post_type, template=template))

    return posts


def build_connection_templates(
    intake: IntakeForm,
    role_name: str,
    career_slug: str,
    top_companies: list[str],
) -> list[str]:
    city = intake.profile.city
    college = intake.profile.college_tier.value
    company = top_companies[0] if top_companies else "your company"
    dream = (
        intake.skills_and_goals.dream_companies[0]
        if intake.skills_and_goals.dream_companies
        else company
    )

    return [
        (
            f"Hi [Name], I'm a {intake.profile.year_of_study.value}-year "
            f"{intake.profile.stream.value} student from {college} ({city}) targeting "
            f"{role_name} roles. I noticed you made the same transition — would you be "
            f"open to a 15-min chat about what actually mattered in your first year?"
        ),
        (
            f"Hi [Name], fellow {city}-based tech grad here. I'm building a {role_name} "
            f"portfolio (SQL/Python/projects) and would value your perspective on "
            f"what hiring managers at Indian startups look for beyond grades."
        ),
        (
            f"Hi [Name], I admire the work {dream} does in [product/data/infra]. "
            f"I'm a fresher focused on {role_name} with public project logs — "
            f"could I ask one question about how your team evaluates portfolios?"
        ),
        (
            f"Hi [Name], I'm actively preparing for {role_name} interviews and saw "
            f"your post on {career_slug.replace('-', ' ')}. I'm documenting weekly "
            f"builds on LinkedIn — would love to connect and learn from your content."
        ),
        (
            f"Hi [Name], I just shipped my first portfolio milestone toward {role_name} "
            f"and your career path resonated. If you have 10 minutes, I'd appreciate "
            f"feedback on whether my GitHub README signals 'job-ready' for {company}-type teams."
        ),
    ]


def build_portfolio(
    intake: IntakeForm,
    career_slug: str,
    role_name: str,
    *,
    projects: ProjectIdeatorOutput | None = None,
    learning_path: LearningPathGeneratorOutput | None = None,
    skill_gap: SkillGapAnalyzerOutput | None = None,
    certifications: CertificationAdvisorOutput | None = None,
    top_hiring_companies: list[str] | None = None,
) -> PortfolioBuilderOutput:
    project_list = projects.projects if projects else []

    return PortfolioBuilderOutput(
        github_readme_md=build_github_readme(
            intake,
            role_name,
            project_list,
            skill_gap,
            certifications,
        ),
        portfolio_site_sections=build_site_sections(
            intake,
            role_name,
            project_list,
            skill_gap,
        ),
        hosting_suggestion=suggest_hosting(project_list, career_slug),
        linkedin_calendar=build_linkedin_calendar(
            role_name,
            career_slug,
            project_list,
            learning_path,
            certifications,
        ),
        connection_request_templates=build_connection_templates(
            intake,
            role_name,
            career_slug,
            top_hiring_companies or [],
        ),
    )
