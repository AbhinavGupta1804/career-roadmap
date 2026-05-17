"""
Agent 6: Certification Advisor — JD corpus cert frequency + budget-aware recommendations.

Recommends certs appearing in ≥15% of JDs OR known to improve callback rates for the role.
Surfaces 2–3 free must-haves, 1 optional paid (if budget), and an explicit DO NOT BUY list.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.schemas.agents import CertificationAdvisorOutput, CertificationItem
from app.schemas.data_models import RoleJdCache
from app.schemas.intake import BudgetInr, IntakeForm
from app.services import data_registry

JD_FREQUENCY_THRESHOLD_PCT = 15.0
MAX_FREE_RECOMMENDED = 3
MAX_PAID_OPTIONAL = 1


@dataclass(frozen=True)
class CertCatalogEntry:
    name: str
    provider: str
    cost: str
    hours: int
    cost_inr_max: int
    tier: Literal["free", "paid"]
    why_jd: str
    why_callback: str | None = None


# Certs that improve callback rates even below 15% JD mention (India fresher market)
CALLBACK_BOOST: dict[str, set[str]] = {
    "data-analyst": {
        "Google Data Analytics Professional Certificate",
        "Microsoft Power BI Data Analyst",
    },
    "data-scientist": {
        "IBM Data Science Professional Certificate",
    },
    "ml-engineer": {
        "Google Professional Machine Learning Engineer",
    },
    "backend-developer": {"AWS Certified Cloud Practitioner"},
    "full-stack-developer": {"AWS Certified Cloud Practitioner"},
    "devops-engineer": {
        "AWS Certified Cloud Practitioner",
        "CKA: Certified Kubernetes Administrator",
    },
    "frontend-developer": {"Meta Front-End Developer Professional Certificate"},
    "ui-ux-designer": {"Google UX Design Professional Certificate"},
    "cybersecurity-analyst": {"CompTIA Security+"},
    "mobile-developer": {"Google Associate Android Developer"},
}

CERT_CATALOG: dict[str, dict[str, CertCatalogEntry]] = {
    "data-analyst": {
        "Google Data Analytics Professional Certificate": CertCatalogEntry(
            name="Google Data Analytics Professional Certificate",
            provider="Coursera (Google)",
            cost="Free (audit) · ~₹2,500 with certificate",
            hours=180,
            cost_inr_max=2500,
            tier="free",
            why_jd="Listed on {pct}% of Data Analyst JDs in our corpus.",
            why_callback="Strong brand signal for Indian analytics fresher screens.",
        ),
        "Microsoft Power BI Data Analyst": CertCatalogEntry(
            name="Microsoft Power BI Data Analyst",
            provider="Microsoft Learn",
            cost="Free learning path · exam ~₹4,500",
            hours=40,
            cost_inr_max=4500,
            tier="paid",
            why_jd="Explicitly preferred in {pct}% of DA JDs (Power BI shops).",
            why_callback="Maps directly to dashboard-heavy DA interviews.",
        ),
        "IBM Data Analyst Professional Certificate": CertCatalogEntry(
            name="IBM Data Analyst Professional Certificate",
            provider="Coursera (IBM)",
            cost="Free (audit)",
            hours=120,
            cost_inr_max=0,
            tier="free",
            why_jd="Mentioned in {pct}% of sampled JDs.",
        ),
    },
    "backend-developer": {
        "AWS Certified Cloud Practitioner": CertCatalogEntry(
            name="AWS Certified Cloud Practitioner",
            provider="AWS",
            cost="Exam ~₹7,000",
            hours=25,
            cost_inr_max=7000,
            tier="paid",
            why_jd="Appears in {pct}% of backend JDs (cloud-native teams).",
            why_callback="Baseline cloud literacy recruiters filter on.",
        ),
        "Oracle Java SE Associate": CertCatalogEntry(
            name="Oracle Java SE Associate",
            provider="Oracle",
            cost="Exam ~₹7,500",
            hours=30,
            cost_inr_max=7500,
            tier="paid",
            why_jd="Referenced in {pct}% of Java-heavy backend JDs.",
        ),
    },
    "devops-engineer": {
        "AWS Certified Cloud Practitioner": CertCatalogEntry(
            name="AWS Certified Cloud Practitioner",
            provider="AWS",
            cost="Exam ~₹7,000",
            hours=25,
            cost_inr_max=7000,
            tier="paid",
            why_jd="{pct}% of DevOps JDs list AWS certs.",
            why_callback="Table-stakes for infra interviews.",
        ),
        "CKA: Certified Kubernetes Administrator": CertCatalogEntry(
            name="CKA: Certified Kubernetes Administrator",
            provider="CNCF",
            cost="Exam ~₹20,000",
            hours=60,
            cost_inr_max=20000,
            tier="paid",
            why_jd="Listed in {pct}% of JDs with K8s ownership.",
        ),
        "HashiCorp Terraform Associate": CertCatalogEntry(
            name="HashiCorp Terraform Associate",
            provider="HashiCorp",
            cost="Exam ~₹4,800",
            hours=20,
            cost_inr_max=4800,
            tier="paid",
            why_jd="IaC cert cited in {pct}% of DevOps postings.",
        ),
    },
    "frontend-developer": {
        "Meta Front-End Developer Professional Certificate": CertCatalogEntry(
            name="Meta Front-End Developer Professional Certificate",
            provider="Coursera (Meta)",
            cost="Free (audit)",
            hours=140,
            cost_inr_max=2500,
            tier="free",
            why_jd="{pct}% of frontend JDs prefer Meta/front-end certs.",
            why_callback="Recognized product-company signal for React roles.",
        ),
    },
    "ml-engineer": {
        "Google Professional Machine Learning Engineer": CertCatalogEntry(
            name="Google Professional Machine Learning Engineer",
            provider="Google Cloud",
            cost="Exam ~₹9,000",
            hours=80,
            cost_inr_max=9000,
            tier="paid",
            why_jd="{pct}% of ML engineer JDs reference Google ML credentials.",
            why_callback="Filters well for ML platform teams.",
        ),
        "TensorFlow Developer Certificate": CertCatalogEntry(
            name="TensorFlow Developer Certificate",
            provider="TensorFlow / Coursera",
            cost="Free (audit)",
            hours=50,
            cost_inr_max=2000,
            tier="free",
            why_jd="Named in {pct}% of ML JDs.",
        ),
    },
    "data-scientist": {
        "IBM Data Science Professional Certificate": CertCatalogEntry(
            name="IBM Data Science Professional Certificate",
            provider="Coursera (IBM)",
            cost="Free (audit)",
            hours=200,
            cost_inr_max=2500,
            tier="free",
            why_jd="{pct}% of data science JDs list IBM/Coursera certs.",
            why_callback="Common fresher DS portfolio anchor in India.",
        ),
    },
    "ui-ux-designer": {
        "Google UX Design Professional Certificate": CertCatalogEntry(
            name="Google UX Design Professional Certificate",
            provider="Coursera (Google)",
            cost="Free (audit)",
            hours=160,
            cost_inr_max=2500,
            tier="free",
            why_jd="{pct}% of UX JDs prefer Google UX cert.",
            why_callback="Helps non-design-degree candidates pass HR screens.",
        ),
    },
    "cybersecurity-analyst": {
        "CompTIA Security+": CertCatalogEntry(
            name="CompTIA Security+",
            provider="CompTIA",
            cost="Exam ~₹25,000",
            hours=50,
            cost_inr_max=25000,
            tier="paid",
            why_jd="{pct}% of security analyst JDs require Security+ or equivalent.",
            why_callback="Industry-standard entry cert for SOC roles.",
        ),
        "Google Cybersecurity Professional Certificate": CertCatalogEntry(
            name="Google Cybersecurity Professional Certificate",
            provider="Coursera (Google)",
            cost="Free (audit)",
            hours=120,
            cost_inr_max=2500,
            tier="free",
            why_jd="Listed in {pct}% of fresher cyber JDs.",
        ),
    },
    "mobile-developer": {
        "Google Associate Android Developer": CertCatalogEntry(
            name="Google Associate Android Developer",
            provider="Google",
            cost="Exam ~₹10,000",
            hours=40,
            cost_inr_max=10000,
            tier="paid",
            why_jd="{pct}% of Android JDs reference Google developer certs.",
            why_callback="Validates Kotlin/Android fundamentals for campus hiring.",
        ),
    },
    "full-stack-developer": {
        "AWS Certified Cloud Practitioner": CertCatalogEntry(
            name="AWS Certified Cloud Practitioner",
            provider="AWS",
            cost="Exam ~₹7,000",
            hours=25,
            cost_inr_max=7000,
            tier="paid",
            why_jd="{pct}% of full-stack JDs mention AWS literacy.",
            why_callback="Signals deploy/hosting awareness beyond tutorials.",
        ),
        "Meta Front-End Developer Professional Certificate": CertCatalogEntry(
            name="Meta Front-End Developer Professional Certificate",
            provider="Coursera (Meta)",
            cost="Free (audit)",
            hours=140,
            cost_inr_max=2500,
            tier="free",
            why_jd="{pct}% of full-stack JDs list front-end cert paths.",
        ),
    },
}

# Explicit DO NOT BUY — not in JD corpus and poor ROI for freshers
SKIP_BY_ROLE: dict[str, list[tuple[str, str]]] = {
    "_global": [
        (
            "Unverified 6-month paid bootcamp (no hiring partners)",
            "Not cited in our JD corpus; high cost with weak placement guarantees for tier-2/3 grads.",
        ),
        (
            "Random Udemy completion certificates (no capstone)",
            "Recruiters discount non-proctored Udemy badges — portfolio projects matter more.",
        ),
        (
            "Generic 'Full Stack Web Development' certificate mills",
            "Zero mentions across 10 JDs per role; skills overlap with free resources.",
        ),
    ],
    "data-analyst": [
        (
            "Generic Data Science bootcamp certificate (non-employer-linked)",
            "DA JDs ask for SQL/BI — not DS bootcamp brands; use projects instead.",
        ),
    ],
    "ml-engineer": [
        (
            "AWS Certified Machine Learning – Specialty (before Cloud Practitioner)",
            "Only ~30% JD mention and too advanced for most freshers; skip until employed.",
        ),
    ],
    "devops-engineer": [
        (
            "Multiple cloud certs at once (Azure + AWS + GCP)",
            "JD corpus centers AWS first — depth beats collecting badges.",
        ),
    ],
}


def build_cert_frequency_map(cache: RoleJdCache) -> dict[str, float]:
    total = len(cache.jds)
    if total == 0:
        return {}

    counts: dict[str, int] = {}
    for jd in cache.jds:
        seen: set[str] = set()
        for cert in jd.certifications_mentioned:
            if cert and cert not in seen:
                seen.add(cert)
                counts[cert] = counts.get(cert, 0) + 1
    return {
        name: round(100.0 * count / total, 1)
        for name, count in counts.items()
    }


def _qualifies(
    cert_name: str,
    freq_pct: float,
    career_slug: str,
) -> bool:
    if freq_pct >= JD_FREQUENCY_THRESHOLD_PCT:
        return True
    boost = CALLBACK_BOOST.get(career_slug, set())
    return cert_name in boost


def _budget_allows_paid(budget: BudgetInr) -> bool:
    return budget in (BudgetInr.MID, BudgetInr.HIGH)


def _format_why(entry: CertCatalogEntry, freq_pct: float) -> str:
    base = entry.why_jd.format(pct=int(freq_pct))
    if entry.why_callback and freq_pct < JD_FREQUENCY_THRESHOLD_PCT:
        return f"{base} {entry.why_callback}"
    if entry.why_callback and freq_pct >= JD_FREQUENCY_THRESHOLD_PCT:
        return f"{base} {entry.why_callback}"
    return base


def _lookup_entry(career_slug: str, cert_name: str) -> CertCatalogEntry | None:
    role_catalog = CERT_CATALOG.get(career_slug, {})
    if cert_name in role_catalog:
        return role_catalog[cert_name]
    for key, entry in role_catalog.items():
        if key.lower() == cert_name.lower():
            return entry
    return None


def advise_certifications(
    intake: IntakeForm,
    career_slug: str,
    *,
    cache: RoleJdCache | None = None,
) -> CertificationAdvisorOutput:
    if cache is None:
        try:
            cache = data_registry.load_jd_cache(career_slug)
        except FileNotFoundError:
            cache = None

    freq: dict[str, float] = build_cert_frequency_map(cache) if cache else {}

    qualified: list[tuple[str, float, CertCatalogEntry]] = []
    for cert_name, pct in sorted(freq.items(), key=lambda x: -x[1]):
        if not _qualifies(cert_name, pct, career_slug):
            continue
        entry = _lookup_entry(career_slug, cert_name)
        if entry:
            qualified.append((cert_name, pct, entry))

    # Callback-boost certs not in JD text yet but in catalog
    for cert_name in CALLBACK_BOOST.get(career_slug, set()):
        if any(q[0] == cert_name for q in qualified):
            continue
        entry = _lookup_entry(career_slug, cert_name)
        if entry:
            qualified.append((cert_name, freq.get(cert_name, 0.0), entry))

    free_picks: list[CertificationItem] = []
    paid_picks: list[CertificationItem] = []

    for _name, pct, entry in qualified:
        item = CertificationItem(
            name=entry.name,
            provider=entry.provider,
            cost=entry.cost,
            hours=entry.hours,
            why=_format_why(entry, pct),
        )
        if entry.tier == "free" or entry.cost_inr_max == 0:
            if len(free_picks) < MAX_FREE_RECOMMENDED:
                free_picks.append(item)
        elif _budget_allows_paid(intake.profile.budget_inr):
            if len(paid_picks) < MAX_PAID_OPTIONAL:
                paid_picks.append(item)

    # Fill free slots from catalog by JD frequency if JD had sparse cert tags
    if len(free_picks) < 2:
        for _name, pct, entry in qualified:
            if entry.tier != "free" and entry.cost_inr_max > 0:
                continue
            if any(p.name == entry.name for p in free_picks):
                continue
            free_picks.append(
                CertificationItem(
                    name=entry.name,
                    provider=entry.provider,
                    cost=entry.cost,
                    hours=entry.hours,
                    why=_format_why(entry, pct),
                ),
            )
            if len(free_picks) >= MAX_FREE_RECOMMENDED:
                break

    recommended = free_picks[:MAX_FREE_RECOMMENDED] + paid_picks[:MAX_PAID_OPTIONAL]

    if not recommended:
        recommended = _fallback_recommendations(career_slug, intake.profile.budget_inr)

    skip: list[dict[str, str]] = []
    seen_skip: set[str] = set()
    for name, why in SKIP_BY_ROLE.get("_global", []):
        skip.append({"name": name, "why_skip": why})
        seen_skip.add(name)
    for name, why in SKIP_BY_ROLE.get(career_slug, []):
        if name not in seen_skip:
            skip.append({"name": name, "why_skip": why})
            seen_skip.add(name)

    # Skip qualified-but-rejected paid when budget is tight
    if not _budget_allows_paid(intake.profile.budget_inr):
        for _name, pct, entry in qualified:
            if entry.tier == "paid" and entry.cost_inr_max > 0:
                skip.append(
                    {
                        "name": entry.name,
                        "why_skip": (
                            f"Appears in {int(pct)}% of JDs but your budget is "
                            f"{intake.profile.budget_inr.value} — prioritize free "
                            "certs and portfolio first."
                        ),
                    }
                )

    return CertificationAdvisorOutput(recommended=recommended, skip=skip)


def _fallback_recommendations(
    career_slug: str,
    budget: BudgetInr,
) -> list[CertificationItem]:
    """When JD cache missing or no cert tags — use role catalog defaults."""
    catalog = CERT_CATALOG.get(career_slug, {})
    items: list[CertificationItem] = []
    for entry in list(catalog.values())[:3]:
        if entry.tier == "paid" and not _budget_allows_paid(budget):
            continue
        items.append(
            CertificationItem(
                name=entry.name,
                provider=entry.provider,
                cost=entry.cost,
                hours=entry.hours,
                why=entry.why_callback or entry.why_jd.format(pct=0),
            )
        )
    return items
