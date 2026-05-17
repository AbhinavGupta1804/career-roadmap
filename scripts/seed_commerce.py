"""Commerce / business seed data: careers, JD roles, skills, certs, companies."""

from __future__ import annotations

# 8 commerce careers → 60 + 8 = 68 total (with base + EXTRA_CAREERS)
COMMERCE_CAREERS = [
    (
        "financial-analyst",
        "Financial Analyst",
        ["Finance & Accounting", "Business Analyst"],
        ["Excel", "Financial modeling", "MIS reporting", "Variance analysis", "Accounting basics"],
        0.76,
        0.70,
        "medium",
        8,
        "medium",
    ),
    (
        "accounts-executive",
        "Accounts Executive",
        ["Finance & Accounting"],
        ["Tally/ERP", "GST basics", "Reconciliation", "Excel", "Voucher entry"],
        0.82,
        0.58,
        "medium",
        5,
        "low",
    ),
    (
        "tax-analyst",
        "Tax Analyst",
        ["Finance & Accounting"],
        ["Income tax basics", "GST", "Excel", "Compliance documentation", "Research"],
        0.70,
        0.65,
        "medium",
        9,
        "medium",
    ),
    (
        "investment-banking-analyst",
        "Investment Banking Analyst (Junior)",
        ["Finance & Accounting", "Business Analyst"],
        ["Excel", "Valuation basics", "Financial statements", "Pitch decks", "Research"],
        0.62,
        0.72,
        "high",
        12,
        "high",
    ),
    (
        "equity-research-associate",
        "Equity Research Associate",
        ["Finance & Accounting", "Data Science"],
        ["Excel", "Financial modeling", "Sector research", "Writing", "Statistics basics"],
        0.58,
        0.74,
        "high",
        11,
        "high",
    ),
    (
        "credit-analyst",
        "Credit Analyst",
        ["Finance & Accounting", "Business Analyst"],
        ["Credit appraisal", "Excel", "Financial ratios", "Risk basics", "Documentation"],
        0.72,
        0.68,
        "medium",
        9,
        "medium",
    ),
    (
        "management-trainee-fmcg",
        "Management Trainee (FMCG / Retail)",
        ["Digital Marketing", "Business Analyst"],
        ["Excel", "Sales analytics", "Distribution basics", "Communication", "Presentation"],
        0.78,
        0.60,
        "medium",
        6,
        "medium",
    ),
    (
        "chartered-accountant-trainee",
        "Chartered Accountant Trainee (Articleship)",
        ["Finance & Accounting"],
        ["Accounting standards", "Audit basics", "Taxation", "Excel", "Documentation"],
        0.85,
        0.55,
        "high",
        10,
        "high",
    ),
]

COMMERCE_RISK: dict[str, tuple] = {
    "financial-analyst": (
        2,
        ["Manual spreadsheet formatting", "Basic chart exports"],
        ["Forecasting judgment", "Business partnering", "MIS design"],
        "FP&A / Business Finance Partner",
        ["Financial modeling", "Storytelling with data", "ERP literacy"],
    ),
    "accounts-executive": (
        3,
        ["Routine voucher entry", "Simple reconciliations"],
        ["Month-end close", "Process controls", "Exception handling"],
        "Finance Operations Specialist",
        ["ERP workflows", "GST compliance", "Automation in Excel"],
    ),
    "tax-analyst": (
        2,
        ["Form-filling busywork", "Generic notice replies"],
        ["Interpretation", "Litigation support prep", "Cross-border awareness"],
        "Tax Advisory Associate",
        ["Research", "Documentation", "Regulatory updates"],
    ),
    "investment-banking-analyst": (
        2,
        ["Slide formatting only", "Data room housekeeping"],
        ["Deal judgment", "Valuation", "Client communication"],
        "Investment Banking Associate",
        ["Modeling", "Sector expertise", "Resilience under deadlines"],
    ),
    "equity-research-associate": (
        2,
        ["Template report drafting", "Data copying from filings"],
        ["Thesis building", "Channel checks", "Risk framing"],
        "Senior Equity Research Analyst",
        ["Modeling", "Writing", "Sector depth"],
    ),
    "credit-analyst": (
        2,
        ["Checklist data entry", "Standard ratio calculators"],
        ["Underwriting judgment", "Sector risk", "Portfolio monitoring"],
        "Credit Risk Manager",
        ["Financial analysis", "Regulatory awareness", "Communication"],
    ),
    "management-trainee-fmcg": (
        2,
        ["Basic sales reporting", "Route plan paperwork"],
        ["Trade marketing", "Category analytics", "Leadership pipeline"],
        "Brand / Category Manager",
        ["Excel", "Field execution", "Stakeholder management"],
    ),
    "chartered-accountant-trainee": (
        2,
        ["Tick-and-tie busywork", "Standard working papers"],
        ["Audit judgment", "Advisory mindset", "Ethics"],
        "Chartered Accountant (Corporate / Advisory)",
        ["Standards depth", "Communication", "Technology in audit"],
    ),
}

# 6 commerce JD caches × 50 = 300 JDs (20 tech + 6 commerce = 26 roles)
COMMERCE_JD_ROLES = [
    "digital-marketing-analyst",
    "financial-analyst",
    "fintech-analyst",
    "supply-chain-analyst",
    "accounts-executive",
    "investment-banking-analyst",
]

COMMERCE_COMPANIES = [
    "Deloitte",
    "EY",
    "PwC",
    "KPMG",
    "HDFC Bank",
    "ICICI Bank",
    "Kotak Mahindra Bank",
    "Axis Bank",
    "HUL",
    "ITC",
    "Asian Paints",
    "Marico",
    "Tata Consumer",
    "Nestlé India",
    "Britannia",
    "Dabur",
    "Colgate-Palmolive",
    "Aditya Birla Capital",
    "Bajaj Finserv",
    "Mahindra Finance",
    "Zerodha",
    "Groww",
    "Policybazaar",
    "Nykaa",
    "DMart",
    "Reliance Retail",
    "TCS BFSI",
    "Wipro BFS",
    "Genpact",
    "WNS",
]

COMMERCE_SKILL_SNIPPETS: dict[str, list[str]] = {
    "digital-marketing-analyst": [
        "Google Analytics",
        "Meta Ads",
        "SQL",
        "Excel",
        "A/B testing",
        "Campaign reporting",
    ],
    "financial-analyst": [
        "Excel",
        "Financial modeling",
        "MIS",
        "Variance analysis",
        "Accounting",
        "PowerPoint",
    ],
    "fintech-analyst": [
        "SQL",
        "Payments",
        "Excel",
        "Risk basics",
        "Dashboards",
        "Regulatory awareness",
    ],
    "supply-chain-analyst": [
        "Excel",
        "SQL",
        "Forecasting",
        "Inventory planning",
        "Operations",
        "Dashboards",
    ],
    "accounts-executive": [
        "Tally",
        "GST",
        "Reconciliation",
        "Excel",
        "ERP",
        "Voucher entry",
    ],
    "investment-banking-analyst": [
        "Excel",
        "Valuation",
        "Financial statements",
        "Pitch decks",
        "Research",
        "PowerPoint",
    ],
}

COMMERCE_CERT_TEMPLATES: dict[str, list[tuple[str, float]]] = {
    "digital-marketing-analyst": [
        ("Google Digital Marketing & E-commerce Certificate", 0.70),
        ("Google Analytics Individual Qualification", 0.45),
        ("Meta Digital Marketing Associate", 0.35),
    ],
    "financial-analyst": [
        ("CFA Level 1 (candidate)", 0.35),
        ("Financial Modeling & Valuation (FMVA-style)", 0.50),
        ("NSE/NISM financial markets certification", 0.40),
    ],
    "fintech-analyst": [
        ("NISM Series certifications", 0.40),
        ("Google Data Analytics Professional Certificate", 0.35),
    ],
    "supply-chain-analyst": [
        ("APICS CSCP fundamentals (awareness)", 0.25),
        ("Six Sigma Yellow Belt", 0.30),
    ],
    "accounts-executive": [
        ("Tally ERP certification", 0.60),
        ("GST practitioner awareness course", 0.45),
    ],
    "investment-banking-analyst": [
        ("CFA Level 1 (candidate)", 0.50),
        ("Financial Modeling & Valuation (FMVA-style)", 0.55),
    ],
}

COMMERCE_RESOURCES = [
    (
        "r-fin-001",
        "Corporate Finance Institute — Excel for Finance (free modules)",
        "https://corporatefinanceinstitute.com/",
        "course",
        "free",
        0,
        15,
        ["Excel", "Financial modeling"],
        "CFI",
    ),
    (
        "r-fin-002",
        "Khan Academy — Finance & capital markets",
        "https://www.khanacademy.org/economics-finance-domain/core-finance",
        "course",
        "free",
        0,
        20,
        ["Accounting basics", "Finance"],
        "Khan Academy",
    ),
    (
        "r-fin-003",
        "NPTEL — Financial Accounting",
        "https://onlinecourses.nptel.ac.in/",
        "course",
        "free",
        0,
        40,
        ["Accounting", "Finance & Accounting"],
        "NPTEL",
    ),
    (
        "r-fin-004",
        "Google Digital Marketing & E-commerce Certificate",
        "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce",
        "course",
        "paid",
        2500,
        60,
        ["Digital Marketing", "Google Analytics"],
        "Coursera",
    ),
    (
        "r-fin-005",
        "TallyPrime learning (official)",
        "https://tallysolutions.com/tally-prime/",
        "doc",
        "free",
        0,
        12,
        ["Tally", "GST"],
        "Tally",
    ),
    (
        "r-fin-006",
        "NSE Academy — financial markets basics",
        "https://www.nseindia.com/learn",
        "course",
        "paid",
        1500,
        25,
        ["Finance", "Markets"],
        "NSE",
    ),
    (
        "r-fin-007",
        "ICAI CA Foundation syllabus overview",
        "https://www.icai.org/post.html?post_id=16418",
        "doc",
        "free",
        0,
        30,
        ["Accounting", "Taxation"],
        "ICAI",
    ),
    (
        "r-fin-008",
        "ExcelIsFun — Excel for accounting playlists",
        "https://www.youtube.com/c/ExcelIsFun",
        "video",
        "free",
        0,
        10,
        ["Excel", "Accounting"],
        "YouTube",
    ),
    (
        "r-fin-009",
        "IIBA ECBA — business analysis fundamentals",
        "https://www.iiba.org/certifications/ecba/",
        "doc",
        "paid",
        15000,
        40,
        ["Business Analyst", "Requirements"],
        "IIBA",
    ),
    (
        "r-fin-010",
        "GST portal — learning resources",
        "https://tutorial.gst.gov.in/",
        "doc",
        "free",
        0,
        8,
        ["GST", "Compliance"],
        "GSTN",
    ),
]

_ROLE_LABELS: dict[str, str] = {
    "digital-marketing-analyst": "Digital Marketing Analyst",
    "financial-analyst": "Financial Analyst",
    "fintech-analyst": "FinTech Product Analyst",
    "supply-chain-analyst": "Supply Chain Analyst",
    "accounts-executive": "Accounts Executive",
    "investment-banking-analyst": "Investment Banking Analyst",
}


def commerce_jd_description(role: str, skills: list[str], cert_clause: str) -> str:
    """Role-specific fresher JD copy for commerce / business roles."""
    label = _ROLE_LABELS.get(role, role.replace("-", " ").title())
    core = ", ".join(skills[:4])
    templates: dict[str, str] = {
        "digital-marketing-analyst": (
            f"Fresher {label} at a growth-focused brand. Own campaign reporting, funnel metrics, "
            f"and A/B test readouts. Strong {core} required; comfort with Excel and SQL for marketing data."
        ),
        "financial-analyst": (
            f"Fresher {label} supporting FP&A / MIS. Build monthly dashboards, variance bridges, "
            f"and management reports. {core} expected; articleship or finance internship is a plus."
        ),
        "fintech-analyst": (
            f"Fresher {label} in payments or lending. Analyze product metrics, reconciliation, "
            f"and regulatory checkpoints. {core} required; interest in Indian fintech compliance helpful."
        ),
        "supply-chain-analyst": (
            f"Fresher {label} for demand planning and inventory. Work on forecasts, OTIF dashboards, "
            f"and vendor coordination. {core} required; operations internship preferred."
        ),
        "accounts-executive": (
            f"Fresher {label} for AP/AR and month-end support. Daily vouchers, reconciliations, "
            f"and GST documentation. {core} required; articleship students welcome."
        ),
        "investment-banking-analyst": (
            f"Fresher {label} (analyst program). Financial modeling support, pitch materials, "
            f"and sector research. {core} required; high Excel proficiency and deadline discipline essential."
        ),
    }
    base = templates.get(
        role,
        f"Fresher {label}. Cross-functional business team. Must know {core}.",
    )
    return f"{base} Portfolio or internships preferred.{cert_clause}"
