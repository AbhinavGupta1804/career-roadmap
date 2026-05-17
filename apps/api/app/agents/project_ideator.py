"""
Agent 5: Project Ideator — 5 JD-aligned portfolio projects (Beginner → Capstone).

No generic todo apps or calculators. Problems mirror cached JD themes for the chosen track.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Literal

from app.agents.skill_gap_analyzer import _canonical_display, _normalize_skill_key
from app.schemas.agents import (
    PortfolioProject,
    ProjectIdeatorOutput,
    SkillGapAnalyzerOutput,
)
from app.schemas.data_models import RoleJdCache
from app.services import data_registry

Difficulty = Literal["Beginner", "Easy", "Medium", "Hard", "Capstone"]
DIFFICULTY_ORDER: list[Difficulty] = [
    "Beginner",
    "Easy",
    "Medium",
    "Hard",
    "Capstone",
]

BANNED_PROJECT_PATTERNS = re.compile(
    r"\b(todo\s*app|to-?do\s+list|calculator\s+app|calculator\s+project)\b",
    re.IGNORECASE,
)

HOURS_BY_DIFFICULTY: dict[Difficulty, int] = {
    "Beginner": 12,
    "Easy": 20,
    "Medium": 30,
    "Hard": 40,
    "Capstone": 60,
}


@dataclass(frozen=True)
class JdThemes:
    role_name: str
    career_slug: str
    top_skills: list[str]
    companies: list[str]
    cities: list[str]
    jd_count: int
    hiring_context: str


def extract_jd_themes(cache: RoleJdCache) -> JdThemes:
    skill_counts: Counter[str] = Counter()
    for jd in cache.jds:
        for skill in jd.skills_mentioned:
            display = _canonical_display(skill)
            skill_counts[display] += 1

    top_skills = [s for s, _ in skill_counts.most_common(8)]
    companies = list(dict.fromkeys(jd.company for jd in cache.jds))[:4]
    cities = list(dict.fromkeys(jd.location for jd in cache.jds))[:3]

    hiring_context = (
        f"Indian tech fresher {cache.role_name} roles "
        f"(JD corpus: {len(cache.jds)} postings; "
        f"themes: cross-functional teams, portfolio or internships preferred)"
    )

    return JdThemes(
        role_name=cache.role_name,
        career_slug=cache.role_slug,
        top_skills=top_skills,
        companies=companies,
        cities=cities,
        jd_count=len(cache.jds),
        hiring_context=hiring_context,
    )


def _themes_from_career_slug(career_slug: str, role_name: str) -> JdThemes:
    career = next(
        c for c in data_registry.load_career_taxonomy().careers if c.slug == career_slug
    )
    skills = [_canonical_display(s) for s in career.required_skills[:6]]
    return JdThemes(
        role_name=role_name,
        career_slug=career_slug,
        top_skills=skills,
        companies=["Razorpay", "Swiggy", "Flipkart"],
        cities=["Bangalore", "Hyderabad"],
        jd_count=0,
        hiring_context=f"Fresher {role_name} hiring in India",
    )


def load_themes(career_slug: str, role_name: str) -> JdThemes:
    try:
        return extract_jd_themes(data_registry.load_jd_cache(career_slug))
    except FileNotFoundError:
        return _themes_from_career_slug(career_slug, role_name)


def _company_sample(themes: JdThemes, index: int = 0) -> str:
    if themes.companies:
        return themes.companies[index % len(themes.companies)]
    return "a growth-stage Indian product company"


def _skill(themes: JdThemes, index: int, fallback: str = "core stack") -> str:
    if themes.top_skills:
        return themes.top_skills[index % len(themes.top_skills)]
    return fallback


def _gap_focus_skills(skill_gap: SkillGapAnalyzerOutput | None, limit: int = 3) -> list[str]:
    if not skill_gap:
        return []
    ranked = sorted(
        skill_gap.skills,
        key=lambda g: (
            {"must": 0, "should": 1, "nice": 2}[g.priority],
            -g.demand_frequency_pct,
            g.weeks_to_bridge,
        ),
    )
    return [g.name for g in ranked if g.weeks_to_bridge > 0][:limit]


def _assert_not_banned(project: PortfolioProject) -> None:
    blob = f"{project.name} {project.problem_statement}"
    if BANNED_PROJECT_PATTERNS.search(blob):
        raise ValueError(f"Banned generic project pattern: {project.name}")


def _build_data_projects(
    themes: JdThemes,
    gap_skills: list[str],
) -> list[PortfolioProject]:
    co = _company_sample(themes)
    s0, s1, s2, s3 = (
        _skill(themes, 0, "SQL"),
        _skill(themes, 1, "Python"),
        _skill(themes, 2, "Excel"),
        _skill(themes, 3, "Power BI"),
    )
    gap_note = gap_skills[0] if gap_skills else s0

    return [
        PortfolioProject(
            name=f"{co}-style ops metrics ({s2} + {s0})",
            difficulty="Beginner",
            problem_statement=(
                f"JD theme: fresher data analyst supporting cross-functional teams. "
                f"Analyze weekly order/refund metrics for a {co}-like Indian fintech ops "
                f"slice using {s2} and {s0} (no toy apps)."
            ),
            dataset_or_api="Synthetic payments ops CSV (GMV, refunds, city)",
            expected_output=f"{s2} workbook + {s0} queries with 3 business insights",
            hours_estimate=HOURS_BY_DIFFICULTY["Beginner"],
            tech_stack=[s2, s0],
            resume_bullet=(
                f"Replicated {co}-style fresher DA work: {s2}/{s0} analysis of GMV & refund "
                f"drivers for cross-functional stakeholders."
            ),
        ),
        PortfolioProject(
            name=f"Cohort retention pipeline ({s1})",
            difficulty="Easy",
            problem_statement=(
                f"Build a {s1} pipeline that loads multi-city transaction logs and outputs "
                f"cohort retention tables — aligned with JD demand for {s1} + {s0}."
            ),
            dataset_or_api="Public e-commerce transactions sample (Kaggle-style)",
            expected_output="Notebook + CSV exports of weekly cohort curves",
            hours_estimate=HOURS_BY_DIFFICULTY["Easy"],
            tech_stack=[s1, s0, "Pandas"],
            resume_bullet=(
                f"Built {s1} cohort retention pipeline mirroring {co}-class product analyst JDs."
            ),
        ),
        PortfolioProject(
            name=f"Executive KPI dashboard ({s3 or s2})",
            difficulty="Medium",
            problem_statement=(
                f"Design a {s3 or s2} dashboard for cross-functional KPIs "
                f"(growth, conversion, support SLA) using JD-highlighted {s0} models."
            ),
            dataset_or_api=f"{s0} warehouse schema + curated metric views",
            expected_output="Interactive dashboard + metric dictionary",
            hours_estimate=HOURS_BY_DIFFICULTY["Medium"],
            tech_stack=[s0, s3 or s2, s1],
            resume_bullet=(
                f"Delivered executive KPI dashboard ({s3 or s2}) backed by {s0} — "
                f"matching {themes.role_name} JD dashboard expectations."
            ),
        ),
        PortfolioProject(
            name=f"Experiment readout ({_skill(themes, 4, 'Statistics')})",
            difficulty="Hard",
            problem_statement=(
                f"Run an A/B experiment analysis for a promo campaign "
                f"({_skill(themes, 4, 'Statistics')} + {s1}) — how Swiggy/Flipkart-style "
                f"growth teams measure lift in fresher DA interviews."
            ),
            dataset_or_api="Simulated experiment assignment + outcome logs",
            expected_output="Readout deck: lift, p-value, guardrail metrics",
            hours_estimate=HOURS_BY_DIFFICULTY["Hard"],
            tech_stack=[s1, s0, _skill(themes, 4, "Statistics")],
            resume_bullet=(
                f"Quantified experiment lift with {s0}/{s1} for a growth campaign readout "
                f"(JD-aligned statistics work)."
            ),
        ),
        PortfolioProject(
            name=f"Capstone: end-to-end metric layer ({gap_note})",
            difficulty="Capstone",
            problem_statement=(
                f"Capstone mirroring {themes.jd_count or 10}+ real JDs: ingest → {s0} semantic "
                f"layer → dashboard + written narrative for hiring managers at "
                f"{', '.join(themes.companies[:3]) or 'target firms'}."
            ),
            dataset_or_api="Multi-table synthetic fintech dataset + README case study",
            expected_output="GitHub repo, dashboard link, 5-slide hiring narrative",
            hours_estimate=HOURS_BY_DIFFICULTY["Capstone"],
            tech_stack=themes.top_skills[:5] or [s0, s1, s2],
            resume_bullet=(
                f"Capstone: end-to-end {themes.role_name} stack ({gap_note}) with metric layer "
                f"and stakeholder-ready story — directly citing JD skill mix."
            ),
        ),
    ]


def _build_backend_projects(themes: JdThemes, gap_skills: list[str]) -> list[PortfolioProject]:
    co = _company_sample(themes)
    py, django, pg, redis = (
        _skill(themes, 0, "Python"),
        _skill(themes, 1, "Django"),
        _skill(themes, 2, "PostgreSQL"),
        _skill(themes, 3, "Redis"),
    )
    return [
        PortfolioProject(
            name=f"REST module for order APIs ({py})",
            difficulty="Beginner",
            problem_statement=(
                f"Implement CRUD REST endpoints for an orders service ({py}/{django}) "
                f"as described in {co}-style backend fresher JDs."
            ),
            dataset_or_api="OpenAPI spec + SQLite/Postgres seed data",
            expected_output="Working API + Postman collection",
            hours_estimate=12,
            tech_stack=[py, django, pg],
            resume_bullet=f"Built {co}-class REST order APIs with {py}/{django} per backend JD stack.",
        ),
        PortfolioProject(
            name=f"Auth + caching layer ({redis})",
            difficulty="Easy",
            problem_statement=(
                f"Add JWT auth and {redis} caching to the order service — common in "
                f"{themes.role_name} JD requirements ({', '.join(themes.top_skills[:4])})."
            ),
            dataset_or_api="Existing order API codebase",
            expected_output="Auth flow docs + cache hit-rate report",
            hours_estimate=20,
            tech_stack=[py, redis, pg],
            resume_bullet=f"Shipped auth + {redis} caching for production-style backend service.",
        ),
        PortfolioProject(
            name=f"Payments webhook worker",
            difficulty="Medium",
            problem_statement=(
                f"Process async payment webhooks with idempotency ({py}, {pg}) — "
                f"mirrors fintech backend JD themes at {co} and peers."
            ),
            dataset_or_api="Simulated Razorpay-style webhook payloads",
            expected_output="Worker service + dead-letter handling",
            hours_estimate=30,
            tech_stack=[py, pg, redis],
            resume_bullet="Implemented idempotent payment webhook worker aligned with Indian fintech JDs.",
        ),
        PortfolioProject(
            name=f"Observed microservice hardening",
            difficulty="Hard",
            problem_statement=(
                f"Add structured logging, health checks, and load tests to the service "
                f"({_skill(themes, 4, 'AWS')} readiness from JD corpus)."
            ),
            dataset_or_api="Docker Compose local stack",
            expected_output="CI job + load-test summary",
            hours_estimate=40,
            tech_stack=[py, "Docker", pg, _skill(themes, 5, "AWS")],
            resume_bullet="Hardened backend microservice with CI load tests — senior fresher JD expectations.",
        ),
        PortfolioProject(
            name="Capstone: deployable backend slice",
            difficulty="Capstone",
            problem_statement=(
                f"Capstone backend feature for cross-functional product squad at "
                f"{', '.join(themes.companies[:2])}: full {django} module with tests & deploy notes."
            ),
            dataset_or_api="Product brief + synthetic user/order domain",
            expected_output="Deployed API + architecture README",
            hours_estimate=60,
            tech_stack=themes.top_skills[:5],
            resume_bullet=(
                f"Capstone: production-grade {themes.role_name} feature matching JD stack "
                f"({gap_skills[0] if gap_skills else py})."
            ),
        ),
    ]


def _build_frontend_projects(themes: JdThemes, gap_skills: list[str]) -> list[PortfolioProject]:
    co = _company_sample(themes)
    react, ts = _skill(themes, 0, "React"), _skill(themes, 1, "TypeScript")
    return [
        PortfolioProject(
            name=f"Component library slice ({react})",
            difficulty="Beginner",
            problem_statement=(
                f"Build accessible UI components for a checkout flow ({react}, HTML, CSS) "
                f"matching {co} frontend fresher JDs."
            ),
            dataset_or_api="Figma-style wireframe PDF",
            expected_output="Storybook or demo page with 5 components",
            hours_estimate=12,
            tech_stack=[react, "HTML", "CSS"],
            resume_bullet=f"Delivered {react} component set for checkout UX per {co}-class JDs.",
        ),
        PortfolioProject(
            name=f"Data-rich table dashboard ({ts})",
            difficulty="Easy",
            problem_statement=(
                f"Implement a sortable/filterable ops table with {ts} — "
                f"frontend JD theme: product metrics for cross-functional teams."
            ),
            dataset_or_api="Mock JSON metrics API",
            expected_output="SPA page + loading/error states",
            hours_estimate=20,
            tech_stack=[react, ts],
            resume_bullet=f"Built {ts} metrics table SPA aligned with {themes.role_name} JD requirements.",
        ),
        PortfolioProject(
            name="Performance & a11y audit",
            difficulty="Medium",
            problem_statement=(
                f"Profile and fix Core Web Vitals on the dashboard ({react}) — "
                f"JD portfolios expect production polish, not demos."
            ),
            dataset_or_api="Lighthouse + WebPageTest",
            expected_output="Before/after perf report",
            hours_estimate=30,
            tech_stack=[react, ts, "Webpack"],
            resume_bullet="Improved CWV and accessibility on metrics dashboard (JD-grade frontend polish).",
        ),
        PortfolioProject(
            name="Feature flag rollout UI",
            difficulty="Hard",
            problem_statement=(
                f"Ship feature-flagged release UI integrating with mock API ({react}/{ts}) "
                f"for growth experiments — common in {co}-style product engineering JDs."
            ),
            dataset_or_api="Mock growth platform API",
            expected_output="Flag admin UI + integration tests",
            hours_estimate=40,
            tech_stack=[react, ts, "Git"],
            resume_bullet="Shipped feature-flag admin UI with tests for experiment-driven product teams.",
        ),
        PortfolioProject(
            name="Capstone: product-facing frontend",
            difficulty="Capstone",
            problem_statement=(
                f"Capstone: end-to-end {themes.role_name} feature for "
                f"{', '.join(themes.companies[:2])} user journey with README case study."
            ),
            dataset_or_api="Product spec + design tokens",
            expected_output="Live demo + portfolio write-up",
            hours_estimate=60,
            tech_stack=themes.top_skills[:5],
            resume_bullet=(
                f"Capstone frontend aligned to JD stack ({gap_skills[0] if gap_skills else react}) "
                f"with hiring-ready case study."
            ),
        ),
    ]


def _build_devops_projects(themes: JdThemes, gap_skills: list[str]) -> list[PortfolioProject]:
    co = _company_sample(themes)
    docker, k8s, aws = (
        _skill(themes, 0, "Docker"),
        _skill(themes, 1, "Kubernetes"),
        _skill(themes, 2, "AWS"),
    )
    return [
        PortfolioProject(
            name=f"Containerized app deploy ({docker})",
            difficulty="Beginner",
            problem_statement=(
                f"Dockerize a sample web service and document runbooks — "
                f"{co} DevOps fresher JD baseline ({docker}, Linux)."
            ),
            dataset_or_api="Sample Python/Node app",
            expected_output="Dockerfile + compose + README",
            hours_estimate=12,
            tech_stack=[docker, "Linux"],
            resume_bullet=f"Containerized service with {docker} per {themes.role_name} JD expectations.",
        ),
        PortfolioProject(
            name=f"CI pipeline ({_skill(themes, 3, 'CI/CD')})",
            difficulty="Easy",
            problem_statement=(
                f"GitHub Actions pipeline: lint, test, build image — JD theme at {co} & peers."
            ),
            dataset_or_api="GitHub repo template",
            expected_output="Green CI badge + pipeline YAML",
            hours_estimate=20,
            tech_stack=["Git", docker, _skill(themes, 3, "CI/CD")],
            resume_bullet="Authored CI pipeline mirroring DevOps JD CI/CD requirements.",
        ),
        PortfolioProject(
            name=f"IaC staging stack ({aws})",
            difficulty="Medium",
            problem_statement=(
                f"Provision staging infra with Terraform/{aws} for a 3-tier app — "
                f"from {themes.jd_count or 10} JD DevOps postings."
            ),
            dataset_or_api="Terraform modules + tfvars sample",
            expected_output="Staging URL + cost estimate",
            hours_estimate=30,
            tech_stack=[aws, _skill(themes, 4, "Terraform"), docker],
            resume_bullet=f"Provisioned {aws} staging via IaC aligned with DevOps JD corpus.",
        ),
        PortfolioProject(
            name=f"{k8s} rollout + probes",
            difficulty="Hard",
            problem_statement=(
                f"Deploy service to {k8s} with readiness/liveness probes and HPA — "
                f"senior fresher SRE/DevOps JD bar."
            ),
            dataset_or_api="kind/minikube cluster",
            expected_output="Helm chart + runbook",
            hours_estimate=40,
            tech_stack=[k8s, docker, "Linux"],
            resume_bullet=f"Deployed resilient {k8s} workload with autoscaling per JD themes.",
        ),
        PortfolioProject(
            name="Capstone: incident-ready platform slice",
            difficulty="Capstone",
            problem_statement=(
                f"Capstone: monitoring + deploy pipeline for {', '.join(themes.companies[:2])}-scale "
                f"platform ({gap_skills[0] if gap_skills else docker})."
            ),
            dataset_or_api="Prometheus/Grafana docker stack",
            expected_output="On-call playbook + demo incident",
            hours_estimate=60,
            tech_stack=themes.top_skills[:5],
            resume_bullet=(
                f"Capstone DevOps platform slice with observability — JD skills: "
                f"{', '.join(themes.top_skills[:4])}."
            ),
        ),
    ]


def _build_ml_projects(themes: JdThemes, gap_skills: list[str]) -> list[PortfolioProject]:
    co = _company_sample(themes)
    py, torch, sql = (
        _skill(themes, 0, "Python"),
        _skill(themes, 1, "PyTorch"),
        _skill(themes, 4, "SQL"),
    )
    return [
        PortfolioProject(
            name=f"Baseline classifier ({py})",
            difficulty="Beginner",
            problem_statement=(
                f"Train a tabular classifier on churn/conv data ({py}, scikit-learn) — "
                f"{co} ML engineer fresher JD entry point."
            ),
            dataset_or_api="Telco churn or similar open dataset",
            expected_output="Notebook with metrics + saved model",
            hours_estimate=12,
            tech_stack=[py, "scikit-learn"],
            resume_bullet=f"Trained baseline ML model ({py}) matching {themes.role_name} JD foundations.",
        ),
        PortfolioProject(
            name=f"Experiment tracking ({torch})",
            difficulty="Easy",
            problem_statement=(
                f"Compare 3 model configs with MLflow-style tracking ({torch}/{py}) — "
                f"JD demand for experiment discipline."
            ),
            dataset_or_api="MNIST or custom tabular set",
            expected_output="Tracking UI screenshots + best run",
            hours_estimate=20,
            tech_stack=[py, torch, "MLflow"],
            resume_bullet="Ran tracked ML experiments per ML engineer JD experiment velocity theme.",
        ),
        PortfolioProject(
            name=f"Feature store slice ({sql})",
            difficulty="Medium",
            problem_statement=(
                f"Build batch features in {sql} feeding a training pipeline — "
                f"aligns with {co}-class ML platform JDs."
            ),
            dataset_or_api="Warehouse-style CSVs",
            expected_output="Feature defs + training script",
            hours_estimate=30,
            tech_stack=[sql, py, docker],
            resume_bullet=f"Built {sql}-backed feature pipeline for ML training (JD-aligned).",
        ),
        PortfolioProject(
            name="Model evaluation harness",
            difficulty="Hard",
            problem_statement=(
                f"Evaluation harness with calibration + slice metrics ({py}) — "
                f"production ML JD theme beyond notebook accuracy."
            ),
            dataset_or_api="Held-out production-like logs",
            expected_output="Eval report by segment",
            hours_estimate=40,
            tech_stack=[py, torch, sql],
            resume_bullet="Shipped ML evaluation harness with slice metrics for production readiness.",
        ),
        PortfolioProject(
            name="Capstone: deployed inference API",
            difficulty="Capstone",
            problem_statement=(
                f"Capstone: containerized inference API for {themes.role_name} at "
                f"{', '.join(themes.companies[:2])} scale with monitoring."
            ),
            dataset_or_api="Trained model artifact + synthetic traffic",
            expected_output="API + Grafana dashboard",
            hours_estimate=60,
            tech_stack=themes.top_skills[:5],
            resume_bullet=(
                f"Capstone ML deployment ({gap_skills[0] if gap_skills else py}) "
                f"mirroring JD stack {', '.join(themes.top_skills[:4])}."
            ),
        ),
    ]


def _build_generic_projects(themes: JdThemes, gap_skills: list[str]) -> list[PortfolioProject]:
    """Fallback builder from JD/career skills only."""
    role = themes.role_name
    skills = themes.top_skills or ["Git", "Communication"]
    co = _company_sample(themes)
    templates = [
        (
            "Beginner",
            f"{co} domain drill ({skills[0]})",
            f"Complete a guided deliverable using {skills[0]} on a {co}-inspired brief "
            f"from real {role} JDs (cross-functional teams).",
        ),
        (
            "Easy",
            f"Integration milestone ({skills[1] if len(skills) > 1 else skills[0]})",
            f"Ship a small integration showcasing {skills[1] if len(skills) > 1 else skills[0]} "
            f"against JD-listed tools.",
        ),
        (
            "Medium",
            f"Production-quality module",
            f"Build a portfolio-ready module combining {', '.join(skills[:3])} — "
            f"matches {themes.jd_count or 'multiple'} JD postings.",
        ),
        (
            "Hard",
            f"Reliability & testing focus",
            f"Add tests, docs, and observability to prior work ({skills[0]}) — "
            f"senior fresher bar in JD corpus.",
        ),
        (
            "Capstone",
            f"Capstone: {role} hiring story",
            f"End-to-end capstone for {', '.join(themes.companies[:2])} with case study "
            f"covering {', '.join(skills[:4])}.",
        ),
    ]
    projects: list[PortfolioProject] = []
    for difficulty, name, problem in templates:
        diff: Difficulty = difficulty  # type: ignore[assignment]
        projects.append(
            PortfolioProject(
                name=name,
                difficulty=diff,
                problem_statement=problem,
                dataset_or_api="Role-specific sample data or public API",
                expected_output="GitHub repo + README case study",
                hours_estimate=HOURS_BY_DIFFICULTY[diff],
                tech_stack=skills[:4],
                resume_bullet=(
                    f"{difficulty} project aligned to {role} JD skills "
                    f"({skills[0]}, {co} context)."
                ),
            )
        )
    return projects


ROLE_BUILDERS: dict[str, Callable[[JdThemes, list[str]], list[PortfolioProject]]] = {
    "data": _build_data_projects,
    "backend": _build_backend_projects,
    "frontend": _build_frontend_projects,
    "fullstack": _build_backend_projects,
    "devops": _build_devops_projects,
    "ml": _build_ml_projects,
    "mobile": _build_frontend_projects,
    "design": _build_generic_projects,
    "security": _build_generic_projects,
}


def _role_family(career_slug: str) -> str:
    if career_slug in ("data-analyst", "data-scientist", "analytics-engineer", "business-analyst-tech"):
        return "data"
    if career_slug == "full-stack-developer":
        return "fullstack"
    if career_slug == "frontend-developer":
        return "frontend"
    if career_slug == "backend-developer":
        return "backend"
    if career_slug in ("devops-engineer", "cloud-engineer", "site-reliability-engineer"):
        return "devops"
    if career_slug in ("ml-engineer", "nlp-engineer", "computer-vision-engineer"):
        return "ml"
    if career_slug == "mobile-developer":
        return "mobile"
    if career_slug in ("ui-ux-designer", "ai-product-designer"):
        return "design"
    if career_slug in ("cybersecurity-analyst", "penetration-tester"):
        return "security"
    return "generic"


def generate_projects(
    career_slug: str,
    role_name: str,
    *,
    skill_gap: SkillGapAnalyzerOutput | None = None,
    themes: JdThemes | None = None,
) -> ProjectIdeatorOutput:
    theme_data = themes or load_themes(career_slug, role_name)
    gap_focus = _gap_focus_skills(skill_gap)
    family = _role_family(career_slug)
    builder = ROLE_BUILDERS.get(family, _build_generic_projects)
    projects = builder(theme_data, gap_focus)

    if len(projects) != 5:
        raise ValueError(f"Expected 5 projects, got {len(projects)}")

    ordered: list[PortfolioProject] = []
    for expected, project in zip(DIFFICULTY_ORDER, projects, strict=True):
        if project.difficulty != expected:
            project = project.model_copy(update={"difficulty": expected})
        _assert_not_banned(project)
        ordered.append(project)

    return ProjectIdeatorOutput(
        role=role_name,
        career_slug=career_slug,
        projects=ordered,
    )


def projects_reference_jd_themes(
    themes: JdThemes,
    projects: list[PortfolioProject],
) -> bool:
    """True if every project mentions at least one top JD skill or hiring company."""
    if not themes.top_skills:
        return True
    for project in projects:
        blob = (
            f"{project.name} {project.problem_statement} "
            f"{project.resume_bullet} {' '.join(project.tech_stack)}"
        ).lower()
        skill_hit = any(s.lower() in blob for s in themes.top_skills)
        company_hit = any(c.lower() in blob for c in themes.companies)
        if not (skill_hit or company_hit):
            return False
    return True


def parse_skill_gap_from_input(agent_input: dict[str, Any]) -> SkillGapAnalyzerOutput | None:
    raw = agent_input.get("skill_gap")
    if not raw:
        return None
    return SkillGapAnalyzerOutput.model_validate(raw)
