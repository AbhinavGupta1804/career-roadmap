"""One-off generator for Step 2 seed JSON. Run from repo root: python scripts/generate_seed_data.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from seed_commerce import (  # noqa: E402
    COMMERCE_CAREERS,
    COMMERCE_COMPANIES,
    COMMERCE_RESOURCES,
    COMMERCE_RISK,
    commerce_jd_description,
)
from seed_expansion import (  # noqa: E402
    EXTRA_CAREERS,
    EXTRA_COMPANIES,
    EXTRA_RISK,
    JD_COUNT,
    JD_ROLES,
    cert_indices_for_role,
    merge_skill_snippets,
)
from seed_commerce import COMMERCE_JD_ROLES  # noqa: E402

DATA = ROOT / "data"
JDS = DATA / "jds"

CAREERS = [
    ("ml-engineer", "ML Engineer", ["Machine Learning", "Data Science"], ["Python", "Linear Algebra", "ML frameworks", "SQL", "Git"], 0.88, 0.95, "high", 10, "high"),
    ("data-scientist", "Data Scientist", ["Data Science", "Machine Learning"], ["Python", "Statistics", "SQL", "Visualization", "ML basics"], 0.82, 0.88, "high", 9, "high"),
    ("data-analyst", "Data Analyst", ["Data Science", "Business Analyst"], ["SQL", "Excel", "Python or R", "Visualization", "Statistics basics"], 0.90, 0.78, "medium", 6, "medium"),
    ("analytics-engineer", "Analytics Engineer", ["Data Science", "Cloud/DevOps"], ["SQL", "dbt", "Python", "Data modeling", "Cloud basics"], 0.85, 0.90, "medium", 8, "high"),
    ("data-engineer", "Data Engineer", ["Data Science", "Cloud/DevOps"], ["SQL", "Python", "Spark", "Airflow", "Cloud"], 0.87, 0.92, "high", 9, "high"),
    ("mlops-engineer", "MLOps Engineer", ["Machine Learning", "Cloud/DevOps"], ["Python", "Docker", "Kubernetes", "ML pipelines", "CI/CD"], 0.80, 0.96, "medium", 10, "high"),
    ("full-stack-developer", "Full-Stack Developer", ["Web Dev"], ["JavaScript", "React", "Node.js", "SQL", "Git"], 0.92, 0.80, "high", 7, "medium"),
    ("frontend-developer", "Frontend Developer", ["Web Dev", "UI/UX Design"], ["HTML", "CSS", "JavaScript", "React", "Git"], 0.88, 0.65, "high", 6, "medium"),
    ("backend-developer", "Backend Developer", ["Web Dev"], ["Python or Java", "REST APIs", "SQL", "System design basics", "Git"], 0.90, 0.82, "high", 7, "medium"),
    ("mobile-developer", "Mobile Developer", ["Mobile Dev", "Web Dev"], ["Kotlin or Swift", "Mobile UI", "APIs", "Git", "App deployment"], 0.75, 0.72, "medium", 8, "medium"),
    ("devops-engineer", "DevOps Engineer", ["Cloud/DevOps"], ["Linux", "Docker", "Kubernetes", "CI/CD", "Cloud"], 0.86, 0.88, "high", 9, "high"),
    ("cloud-engineer", "Cloud Engineer", ["Cloud/DevOps"], ["AWS or Azure", "Networking", "IaC", "Linux", "Security basics"], 0.84, 0.90, "high", 9, "high"),
    ("site-reliability-engineer", "Site Reliability Engineer (SRE)", ["Cloud/DevOps"], ["Linux", "Monitoring", "Python/Go", "Kubernetes", "Incident response"], 0.78, 0.91, "medium", 10, "high"),
    ("cybersecurity-analyst", "Cybersecurity Analyst", ["Cybersecurity"], ["Networking", "Linux", "SIEM", "Threat analysis", "Scripting"], 0.83, 0.85, "medium", 9, "high"),
    ("penetration-tester", "Penetration Tester", ["Cybersecurity"], ["Networking", "Web security", "Linux", "Burp Suite", "Reporting"], 0.70, 0.80, "medium", 10, "high"),
    ("ui-ux-designer", "UI/UX Designer", ["UI/UX Design"], ["Figma", "User research", "Wireframing", "Prototyping", "Design systems"], 0.80, 0.70, "high", 7, "medium"),
    ("ai-product-designer", "AI Product Designer", ["UI/UX Design", "Machine Learning"], ["Figma", "UX research", "AI product patterns", "Prototyping", "Collaboration"], 0.72, 0.94, "medium", 9, "high"),
    ("product-manager-tech", "Product Manager (Tech)", ["Product Management"], ["Product sense", "SQL basics", "User research", "Roadmapping", "Communication"], 0.78, 0.82, "high", 10, "high"),
    ("qa-automation-engineer", "QA Automation Engineer", ["Web Dev", "Cloud/DevOps"], ["Manual testing", "Selenium/Playwright", "Python/Java", "API testing", "CI"], 0.76, 0.75, "medium", 7, "medium"),
    ("embedded-systems-engineer", "Embedded Systems Engineer", ["Hardware", "Robotics"], ["C/C++", "Microcontrollers", "RTOS", "Debugging", "Electronics basics"], 0.65, 0.78, "medium", 10, "high"),
    ("game-developer", "Game Developer", ["Game Dev"], ["C# or C++", "Unity/Unreal", "Game math", "Physics basics", "Git"], 0.60, 0.68, "medium", 10, "high"),
    ("robotics-software-engineer", "Robotics Software Engineer", ["Robotics", "Machine Learning"], ["Python", "C++", "ROS", "Kinematics basics", "Computer vision basics"], 0.62, 0.86, "medium", 11, "high"),
    ("technical-writer", "Technical Writer (Developer Docs)", ["Web Dev"], ["Writing", "Markdown", "API docs", "Developer tools", "Information architecture"], 0.55, 0.72, "low", 6, "medium"),
    ("business-analyst-tech", "Business Analyst (Tech)", ["Business Analyst", "Finance & Accounting", "Data Science"], ["SQL", "Excel", "Requirements", "Process mapping", "Stakeholder communication"], 0.74, 0.76, "medium", 7, "medium"),
    ("database-administrator", "Database Administrator", ["Cloud/DevOps", "Data Science"], ["SQL", "PostgreSQL/MySQL", "Backup/restore", "Performance tuning", "Security"], 0.68, 0.74, "medium", 9, "medium"),
    ("network-engineer", "Network Engineer", ["Cybersecurity", "Hardware"], ["Networking", "Routing/Switching", "Firewalls", "Linux", "Monitoring"], 0.66, 0.70, "medium", 9, "high"),
    ("solutions-engineer", "Solutions Engineer", ["Web Dev", "Product Management"], ["SQL", "APIs", "Presentation", "Debugging", "Customer discovery"], 0.70, 0.83, "medium", 8, "medium"),
    ("computer-vision-engineer", "Computer Vision Engineer", ["Machine Learning", "Robotics"], ["Python", "OpenCV", "Deep learning", "Linear algebra", "Deployment"], 0.68, 0.93, "medium", 10, "high"),
    ("nlp-engineer", "NLP Engineer", ["Machine Learning", "Data Science"], ["Python", "Transformers", "NLP fundamentals", "SQL", "MLOps basics"], 0.70, 0.94, "medium", 10, "high"),
    ("iot-developer", "IoT Developer", ["Hardware", "Cloud/DevOps"], ["C/C++", "Embedded Linux", "MQTT", "Cloud IoT", "Sensors"], 0.58, 0.80, "low", 9, "medium"),
    # Tier 4 — heavily disrupted (for do-not-pursue callouts; excluded from Agent 1 picks)
    ("generic-content-writer", "Generic Content Writer", ["Marketing", "Web Dev"], ["Writing", "SEO basics", "Google Docs", "Keyword research"], 0.35, 0.22, "high", 4, "low"),
    ("junior-graphic-designer", "Junior Graphic Designer (Agency)", ["UI/UX Design", "Marketing"], ["Photoshop", "Canva", "Basic layouts", "Social creatives"], 0.40, 0.18, "high", 5, "low"),
    ("manual-qa-tester", "Manual QA Tester", ["Web Dev"], ["Test cases", "Excel", "Bug reporting", "Attention to detail"], 0.42, 0.25, "medium", 4, "low"),
    ("tier-1-tech-support", "Tier-1 Tech Support", ["Web Dev", "Cybersecurity"], ["Troubleshooting scripts", "CRM tools", "Communication", "Ticketing"], 0.38, 0.20, "medium", 3, "low"),
    # Tier 5 — sunset (freshers should not pursue as primary path)
    ("bpo-voice-agent", "BPO / Call Center Voice Agent", ["Sales", "Business Analyst"], ["Scripts", "CRM", "English communication", "Attendance"], 0.25, 0.08, "low", 3, "low"),
    ("generic-seo-writer", "Generic SEO Content Mill Writer", ["Marketing", "Web Dev"], ["SEO templates", "Surfer/Clearscope basics", "WordPress", "Plagiarism tools"], 0.28, 0.10, "high", 3, "low"),
    ("microstock-design-seller", "Microstock / Fiverr Logo Seller", ["UI/UX Design", "Marketing"], ["Canva", "Stock templates", "Basic Illustrator", "Client chat"], 0.22, 0.06, "high", 3, "low"),
    ("data-entry-operator", "Data Entry Operator", ["Business Analyst", "Hardware"], ["Typing speed", "Excel", "Accuracy", "Basic English"], 0.20, 0.05, "low", 3, "low"),
] + EXTRA_CAREERS + COMMERCE_CAREERS

# Low salary bands for tier 4/5 roles
LOW_SALARY_SLUGS = {
    "generic-content-writer",
    "junior-graphic-designer",
    "manual-qa-tester",
    "tier-1-tech-support",
    "bpo-voice-agent",
    "generic-seo-writer",
    "microstock-design-seller",
    "data-entry-operator",
}

RISK = {
    "ml-engineer": (1, ["Manual feature tuning only", "Notebook-only prototyping"], ["Experiment velocity", "Production ML systems"], "AI Systems Engineer", ["MLOps", "Evaluation design", "System thinking"]),
    "data-scientist": (2, ["Exploratory analysis busywork"], ["Hypothesis framing", "Experiment design"], "Decision Scientist", ["Business communication", "Causal thinking"]),
    "data-analyst": (2, ["Ad-hoc SQL generation", "Basic charting"], ["Metric definition", "Storytelling"], "Analytics Strategist", ["Domain knowledge", "Stakeholder influence"]),
    "analytics-engineer": (1, ["Hand-written pipeline glue"], ["Reliable data models", "Semantic layers"], "Data Platform Engineer", ["dbt", "Data contracts", "SQL depth"]),
    "data-engineer": (1, ["Boilerplate ETL scripts"], ["Pipeline reliability", "Cost optimization"], "Data Platform Architect", ["Streaming", "Governance", "Cloud"]),
    "mlops-engineer": (1, ["Manual deploy steps"], ["Automated ML lifecycle"], "AI Platform Engineer", ["K8s", "Observability", "Model governance"]),
    "full-stack-developer": (2, ["CRUD scaffolding", "Simple UI generation"], ["End-to-end ownership", "Product judgment"], "Product Engineer", ["System design", "UX sense"]),
    "frontend-developer": (3, ["Pixel-perfect static pages", "Basic component boilerplate"], ["Complex interaction design", "Performance"], "Frontend Platform Engineer", ["Accessibility", "Design systems", "Core Web Vitals"]),
    "backend-developer": (2, ["Boilerplate API code"], ["Distributed systems", "Security"], "Backend Platform Engineer", ["System design", "Databases", "Auth"]),
    "mobile-developer": (2, ["Simple UI screens"], ["Native performance", "Offline-first UX"], "Mobile Platform Engineer", ["Architecture", "Store policies"]),
    "devops-engineer": (2, ["Repetitive infra scripts"], ["Reliability engineering", "Incident response"], "Platform Reliability Engineer", ["SRE practices", "IaC", "Security"]),
    "cloud-engineer": (1, ["Manual console clicks"], ["Architecture design", "FinOps"], "Cloud Architect", ["Multi-cloud", "Security", "Automation"]),
    "site-reliability-engineer": (1, ["Manual runbooks only"], ["Automation", "Observability"], "Reliability Architect", ["SLO design", "Chaos engineering"]),
    "cybersecurity-analyst": (2, ["Tier-1 alert triage"], ["Threat hunting", "Incident leadership"], "Security Operations Lead", ["Detection engineering", "GRC awareness"]),
    "penetration-tester": (2, ["Checklist scanning only"], ["Creative attack paths", "Risk communication"], "Offensive Security Consultant", ["AppSec depth", "Red team ops"]),
    "ui-ux-designer": (2, ["Generic wireframes", "Stock UI kits"], ["Research-led design", "Systems thinking"], "Product Design Lead", ["Research", "Interaction design"]),
    "ai-product-designer": (1, ["Static mockups only"], ["Agent UX", "Trust design"], "AI Interaction Designer", ["Model behavior literacy", "Prototyping"]),
    "product-manager-tech": (2, ["Status doc writing"], ["Prioritization", "User insight"], "AI Product Lead", ["Data literacy", "Technical fluency"]),
    "qa-automation-engineer": (3, ["Manual regression only"], ["Test architecture", "CI quality gates"], "Quality Engineering Lead", ["Automation frameworks", "API testing"]),
    "embedded-systems-engineer": (2, ["Simple firmware templates"], ["Hardware-software co-design"], "Embedded Platform Engineer", ["RTOS", "Debugging", "C/C++"]),
    "game-developer": (2, ["Asset placement busywork"], ["Gameplay feel", "Performance"], "Technical Game Designer", ["Engine depth", "Math"]),
    "robotics-software-engineer": (1, ["Teleoperation scripts only"], ["Perception + planning stacks"], "Autonomy Engineer", ["ROS2", "CV", "Controls basics"]),
    "technical-writer": (2, ["First-draft docs"], ["Information architecture", "Developer empathy"], "Developer Experience Lead", ["API clarity", "Docs-as-code"]),
    "business-analyst-tech": (2, ["Slide formatting", "Basic reporting"], ["Requirements clarity", "Process redesign"], "Product Operations Analyst", ["SQL", "Domain expertise"]),
    "database-administrator": (3, ["Routine backup scripts"], ["Performance tuning", "HA design"], "Data Reliability Engineer", ["PostgreSQL internals", "Cloud DB"]),
    "network-engineer": (2, ["Cable-label busywork"], ["Architecture", "Automation"], "Network Automation Engineer", ["Python", "SDN basics"]),
    "solutions-engineer": (2, ["Demo script reading"], ["Technical discovery", "POC design"], "Customer Engineering Lead", ["APIs", "Presentation"]),
    "computer-vision-engineer": (1, ["Labeling-only workflows"], ["Model + edge deployment"], "Vision Systems Engineer", ["CV pipelines", "Deployment"]),
    "nlp-engineer": (1, ["Simple chatbot wrappers"], ["RAG systems", "Evaluation"], "LLM Application Engineer", ["Prompt systems", "Safety"]),
    "iot-developer": (2, ["Basic sensor polling scripts"], ["Edge + cloud integration"], "Edge IoT Engineer", ["MQTT", "Security", "Embedded Linux"]),
    # Tier 4 — heavily disrupted
    "generic-content-writer": (
        4,
        ["Bulk blog generation", "Outline spinning", "Generic listicles"],
        ["Editorial judgment", "Brand voice", "Original reporting"],
        "Content Strategist (AI-assisted)",
        ["Niche expertise", "Interview skills", "Fact-checking"],
    ),
    "junior-graphic-designer": (
        4,
        ["Template resizing", "Stock asset assembly", "Basic social banners"],
        ["Brand systems", "Motion storytelling", "Design research"],
        "Visual Designer (AI-native workflows)",
        ["Figma systems", "Design thinking", "Cross-functional collaboration"],
    ),
    "manual-qa-tester": (
        4,
        ["Repetitive click-path regression", "Screenshot comparison"],
        ["Test strategy", "Exploratory testing", "Production incident learning"],
        "Quality Engineer",
        ["Test automation", "API testing", "CI/CD quality gates"],
    ),
    "tier-1-tech-support": (
        4,
        ["Scripted troubleshooting", "Password resets", "Ticket categorization"],
        ["Complex diagnostics", "Customer empathy", "Root-cause analysis"],
        "Technical Support Engineer (L2/L3)",
        ["Systems knowledge", "Networking basics", "Documentation"],
    ),
    # Tier 5 — sunset
    "bpo-voice-agent": (
        5,
        ["Script reading", "Outbound dialing", "Basic objection handling"],
        ["Consultative sales", "Domain expertise"],
        "Customer Success (product-led)",
        ["Upskilling into tech support or inside sales with product knowledge"],
    ),
    "generic-seo-writer": (
        5,
        ["Mass-produced SEO articles", "AI-generated filler content"],
        ["Technical SEO strategy", "Product-led content"],
        "SEO Content Strategist",
        ["Analytics", "Subject-matter depth", "Distribution"],
    ),
    "microstock-design-seller": (
        5,
        ["$5 logo templates", "Stock icon packs", "AI-generated assets"],
        ["Brand identity systems", "Product design"],
        "Brand / Product Designer",
        ["Portfolio depth", "Design systems", "UX fundamentals"],
    ),
    "data-entry-operator": (
        5,
        ["Form filling", "Copy-paste between systems", "OCR cleanup"],
        ["Process automation", "Data operations"],
        "Data Operations / Analyst",
        ["SQL", "Python automation", "Excel power-user skills"],
    ),
    **EXTRA_RISK,
    **COMMERCE_RISK,
}

TIER_DEFS = {
    "1": {"label": "AI Tailwind", "description": "Role created or expanded by AI. Demand growing."},
    "2": {"label": "AI-Augmented", "description": "Human + AI beats either alone. Lazy practitioners lose."},
    "3": {"label": "Partially Displaced", "description": "Entry tasks automated; senior roles safer. Harder to break in."},
    "4": {"label": "Heavily Disrupted", "description": "Most roles automated in 2–4 years."},
    "5": {"label": "Sunset", "description": "Wiped out for freshers within ~5 years."},
}

COMPANIES = list(dict.fromkeys(EXTRA_COMPANIES + COMMERCE_COMPANIES))
CITIES = ["Bangalore", "Hyderabad", "Pune", "Mumbai", "Gurgaon", "Chennai", "Remote", "Noida", "Kochi"]

SKILL_SNIPPETS = merge_skill_snippets({
    "data-analyst": ["SQL", "Python", "Excel", "Power BI", "Tableau", "Statistics"],
    "full-stack-developer": ["JavaScript", "React", "Node.js", "MongoDB", "REST APIs", "Git"],
    "ml-engineer": ["Python", "PyTorch", "scikit-learn", "MLflow", "SQL", "Docker"],
    "frontend-developer": ["React", "TypeScript", "CSS", "HTML", "Git", "Webpack"],
    "backend-developer": ["Python", "Django", "PostgreSQL", "Redis", "REST", "AWS"],
    "devops-engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform"],
    "data-scientist": ["Python", "Pandas", "SQL", "Statistics", "ML", "Visualization"],
    "ui-ux-designer": ["Figma", "User research", "Wireframes", "Prototyping", "Design systems"],
    "cybersecurity-analyst": ["SIEM", "Networking", "Linux", "Incident response", "Python"],
    "mobile-developer": ["Kotlin", "Android", "REST APIs", "Firebase", "Git"],
})


def salary_bands(high: bool = False, sunset: bool = False) -> dict:
    if sunset:
        return {
            "tier_1": {"min_lpa": 4, "max_lpa": 7},
            "tier_2": {"min_lpa": 2.5, "max_lpa": 4.5},
            "tier_3": {"min_lpa": 1.8, "max_lpa": 3.5},
        }
    if high:
        return {
            "tier_1": {"min_lpa": 12, "max_lpa": 28},
            "tier_2": {"min_lpa": 6, "max_lpa": 14},
            "tier_3": {"min_lpa": 3.5, "max_lpa": 8},
        }
    return {
        "tier_1": {"min_lpa": 10, "max_lpa": 22},
        "tier_2": {"min_lpa": 5, "max_lpa": 12},
        "tier_3": {"min_lpa": 3, "max_lpa": 7},
    }


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    JDS.mkdir(parents=True, exist_ok=True)

    careers_out = {
        "version": "2026.1",
        "careers": [],
    }
    for row in CAREERS:
        slug, name, tags, skills, demand, resilience, comp, months, diff = row
        careers_out["careers"].append({
            "slug": slug,
            "name": name,
            "interest_tags": tags,
            "required_skills": skills,
            "salary_bands": salary_bands(
                high=slug in {"ml-engineer", "data-scientist", "mlops-engineer", "ai-product-designer", "nlp-engineer"},
                sunset=slug in LOW_SALARY_SLUGS,
            ),
            "market_demand_index": demand,
            "ai_resilience_index": resilience,
            "competition_level": comp,
            "typical_months_to_job": months,
            "entry_difficulty": diff,
        })

    risk_out = {
        "version": "2026.1",
        "tier_definitions": TIER_DEFS,
        "careers": {},
    }
    for slug, (tier, replaces, amplifies, evolved, survival) in RISK.items():
        risk_out["careers"][slug] = {
            "tier": tier,
            "replaces": replaces,
            "amplifies": amplifies,
            "evolved_role_2029": evolved,
            "survival_skills": survival,
        }

    (DATA / "careers.json").write_text(json.dumps(careers_out, indent=2), encoding="utf-8")
    (DATA / "ai-risk-tiers.json").write_text(json.dumps(risk_out, indent=2), encoding="utf-8")

    for role in JD_ROLES:
        skills = SKILL_SNIPPETS.get(
            role,
            ["Communication", "Problem solving", "Git", "SQL", "Python", "Teamwork"],
        )
        cert_by_jd: dict[int, list[str]] = {i: [] for i in range(JD_COUNT)}
        for cert_name, indices in cert_indices_for_role(role, JD_COUNT):
            for idx in indices:
                if 0 <= idx < JD_COUNT:
                    cert_by_jd[idx].append(cert_name)
        jds = []
        for i in range(JD_COUNT):
            certs = cert_by_jd[i]
            cert_clause = (
                f" Preferred certifications: {', '.join(certs)}."
                if certs
                else ""
            )
            if role in COMMERCE_JD_ROLES:
                description = commerce_jd_description(role, skills, cert_clause)
            else:
                description = (
                    f"Fresher {role.replace('-', ' ')} role. Work with cross-functional teams. "
                    f"Must know {', '.join(skills[:4])}. Portfolio or internships preferred."
                    f"{cert_clause}"
                )
            jds.append({
                "id": f"{role}-{i+1:02d}",
                "role_slug": role,
                "title": role.replace("-", " ").title(),
                "company": COMPANIES[i % len(COMPANIES)],
                "location": CITIES[i % len(CITIES)],
                "experience_level": "fresher",
                "description": description,
                "skills_mentioned": skills,
                "certifications_mentioned": certs,
            })
        cache = {
            "role_slug": role,
            "role_name": role.replace("-", " ").title(),
            "jds": jds,
        }
        (JDS / f"{role}.json").write_text(json.dumps(cache, indent=2), encoding="utf-8")

    resources = _build_resources()
    (DATA / "resources.json").write_text(json.dumps(resources, indent=2), encoding="utf-8")
    print("Generated:", DATA)
    print("Careers:", len(careers_out["careers"]))
    print("JD roles:", len(JD_ROLES))
    print("JDs per role:", JD_COUNT)
    print("Total JDs:", len(JD_ROLES) * JD_COUNT)
    print("Resources:", len(resources["resources"]))


def _build_resources() -> dict:
    items = [
        ("r-py-001", "Python for Everybody (Coursera audit)", "https://www.coursera.org/specializations/python", "course", "free", 0, 60, ["Python"], "Coursera"),
        ("r-py-002", "Core Python Tutorial", "https://docs.python.org/3/tutorial/", "doc", "free", 0, 20, ["Python"], "Python docs"),
        ("r-sql-001", "SQLBolt", "https://sqlbolt.com/", "doc", "free", 0, 12, ["SQL"], "SQLBolt"),
        ("r-sql-002", "Mode SQL Tutorial", "https://mode.com/sql-tutorial/", "doc", "free", 0, 15, ["SQL"], "Mode"),
        ("r-ds-001", "NPTEL Data Science for Engineers", "https://onlinecourses.nptel.ac.in/noc26_cs101", "course", "free", 0, 40, ["Statistics", "Python"], "NPTEL"),
        ("r-ml-001", "Andrew Ng ML Specialization", "https://www.coursera.org/specializations/machine-learning-introduction", "course", "paid", 3000, 80, ["ML basics", "Python"], "Coursera"),
        ("r-ml-002", "fast.ai Practical Deep Learning", "https://course.fast.ai/", "course", "free", 0, 50, ["Deep learning", "Python"], "fast.ai"),
        ("r-fe-001", "freeCodeCamp Responsive Web Design", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "course", "free", 0, 40, ["HTML", "CSS"], "freeCodeCamp"),
        ("r-fe-002", "React Official Docs", "https://react.dev/learn", "doc", "free", 0, 25, ["React", "JavaScript"], "Meta"),
        ("r-fe-003", "Traversy Media React Crash Course", "https://www.youtube.com/watch?v=w7ejDZ8SWv8", "video", "free", 0, 2, ["React"], "YouTube"),
        ("r-be-001", "FastAPI Documentation", "https://fastapi.tiangolo.com/", "doc", "free", 0, 15, ["REST APIs", "Python"], "FastAPI"),
        ("r-be-002", "Node.js Express Getting Started", "https://expressjs.com/en/starter/installing.html", "doc", "free", 0, 10, ["Node.js", "REST APIs"], "Express"),
        ("r-git-001", "Git & GitHub Crash Course", "https://www.youtube.com/watch?v=RGOj5yxtSMs", "video", "free", 0, 1, ["Git"], "YouTube"),
        ("r-dv-001", "Docker for Beginners", "https://www.youtube.com/watch?v=fqMOX6JJhGo", "video", "free", 0, 2, ["Docker"], "YouTube"),
        ("r-dv-002", "KodeKloud Kubernetes Basics (free labs)", "https://kodekloud.com/free-labs/kubernetes", "course", "free", 0, 20, ["Kubernetes"], "KodeKloud"),
        ("r-cl-001", "AWS Cloud Practitioner Essentials", "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "course", "free", 0, 12, ["AWS"], "AWS"),
        ("r-ux-001", "Google UX Design Certificate (audit)", "https://www.coursera.org/professional-certificates/google-ux-design", "course", "paid", 2500, 100, ["Figma", "User research"], "Coursera"),
        ("r-ux-002", "Figma Learn", "https://www.figma.com/resource-library/", "doc", "free", 0, 10, ["Figma"], "Figma"),
        ("r-cy-001", "TryHackMe Pre Security", "https://tryhackme.com/path/outline/presecurity", "course", "free", 0, 25, ["Cybersecurity basics"], "TryHackMe"),
        ("r-da-001", "Alex the Analyst SQL Playlist", "https://www.youtube.com/playlist?list=PLUaB-1hzbeCeDmIzsN-SwxUc8YaypqYWV", "video", "free", 0, 8, ["SQL", "Excel"], "YouTube"),
        ("r-da-002", "Power BI Desktop Docs", "https://learn.microsoft.com/en-us/power-bi/", "doc", "free", 0, 15, ["Power BI", "Visualization"], "Microsoft"),
        ("r-mob-001", "Android Basics with Compose", "https://developer.android.com/courses/android-basics-compose/course", "course", "free", 0, 30, ["Kotlin", "Android"], "Google"),
        ("r-stat-001", "Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "course", "free", 0, 25, ["Statistics"], "Khan Academy"),
        ("r-la-001", "3Blue1Brown Linear Algebra", "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr", "video", "free", 0, 6, ["Linear Algebra"], "YouTube"),
        ("r-dbt-001", "dbt Learn", "https://courses.getdbt.com/courses/fundamentals", "course", "free", 0, 12, ["dbt", "SQL"], "dbt Labs"),
        ("r-llm-001", "Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course/chapter1/1", "course", "free", 0, 30, ["NLP fundamentals"], "Hugging Face"),
        ("r-cv-001", "OpenCV Python Tutorials", "https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html", "doc", "free", 0, 20, ["OpenCV", "Python"], "OpenCV"),
        ("r-ros-001", "ROS2 Humble Tutorials", "https://docs.ros.org/en/humble/Tutorials.html", "doc", "free", 0, 25, ["ROS"], "Open Robotics"),
        ("r-pm-001", "Inspired (book summary + notes)", "https://www.youtube.com/watch?v=9jkzd02IkFc", "video", "free", 0, 1, ["Product sense"], "YouTube"),
        ("r-ud-001", "Udemy sale courses (SQL/Python)", "https://www.udemy.com/courses/search/?q=sql+python", "course", "paid", 500, 20, ["SQL", "Python"], "Udemy"),
        ("r-npt-001", "NPTEL Programming in Java", "https://onlinecourses.nptel.ac.in/noc26_cs42", "course", "free", 0, 45, ["Java"], "NPTEL"),
        ("r-ts-001", "TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/", "doc", "free", 0, 12, ["TypeScript", "JavaScript"], "Microsoft"),
        ("r-k8-001", "Kubernetes Official Docs Concepts", "https://kubernetes.io/docs/concepts/", "doc", "free", 0, 18, ["Kubernetes"], "CNCF"),
        ("r-fig-001", "Refactoring UI (principles)", "https://www.refactoringui.com/", "book", "paid", 1500, 6, ["UI/UX Design"], "Refactoring UI"),
        ("r-api-001", "Postman API Fundamentals", "https://learning.postman.com/docs/getting-started/introduction/", "doc", "free", 0, 5, ["REST APIs"], "Postman"),
        ("r-linux-001", "Linux Journey", "https://linuxjourney.com/", "doc", "free", 0, 15, ["Linux"], "Linux Journey"),
        ("r-net-001", "Cisco Networking Basics", "https://skillsforall.com/course/networking-basics", "course", "free", 0, 20, ["Networking"], "Cisco"),
        ("r-embed-001", "Embedded Systems - NPTEL", "https://onlinecourses.nptel.ac.in/noc26_ee101", "course", "free", 0, 40, ["C/C++", "Embedded"], "NPTEL"),
        ("r-game-001", "Brackeys Unity tutorials (archived)", "https://www.youtube.com/@Brackeys", "video", "free", 0, 10, ["Unity", "C#"], "YouTube"),
        ("r-write-001", "Google Developer Documentation Style Guide", "https://developers.google.com/style", "doc", "free", 0, 8, ["Technical writing"], "Google"),
        ("r-ba-001", "Business Analysis fundamentals (Coursera audit)", "https://www.coursera.org/specializations/business-analytics", "course", "paid", 2000, 40, ["Business analysis", "Excel"], "Coursera"),
        ("r-pg-001", "PostgreSQL Tutorial", "https://www.postgresqltutorial.com/", "doc", "free", 0, 15, ["PostgreSQL", "SQL"], "postgresqltutorial.com"),
        ("r-mongo-001", "MongoDB University M001", "https://learn.mongodb.com/courses/mongodb-basics", "course", "free", 0, 12, ["MongoDB"], "MongoDB"),
        ("r-terraform-001", "Terraform Getting Started", "https://developer.hashicorp.com/terraform/tutorials/aws-get-started", "doc", "free", 0, 10, ["Terraform", "AWS"], "HashiCorp"),
        ("r-play-001", "Playwright Getting Started", "https://playwright.dev/docs/intro", "doc", "free", 0, 8, ["QA Automation"], "Microsoft"),
        ("r-rag-001", "DeepLearning.AI LangChain short courses", "https://www.deeplearning.ai/short-courses/", "course", "free", 0, 6, ["LLM applications", "RAG"], "DeepLearning.AI"),
        ("r-port-001", "GitHub Pages Docs", "https://docs.github.com/en/pages", "doc", "free", 0, 2, ["Git", "Portfolio"], "GitHub"),
        ("r-comm-001", "Technical communication for engineers", "https://www.coursera.org/learn/communication-skills-engineers", "course", "free", 0, 10, ["Communication"], "Coursera"),
    ] + list(COMMERCE_RESOURCES)
    return {
        "version": "2026.1",
        "resources": [
            {
                "id": rid,
                "title": title,
                "url": url,
                "type": rtype,
                "cost": cost,
                "cost_inr_max": cost_max,
                "hours": hours,
                "skills_taught": skills,
                "provider": provider,
            }
            for rid, title, url, rtype, cost, cost_max, hours, skills, provider in items
        ],
    }


if __name__ == "__main__":
    main()
