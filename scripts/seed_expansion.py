"""Additional careers and JD generation helpers (60+ careers, 26×50 JDs with commerce)."""

from __future__ import annotations

from seed_commerce import COMMERCE_CERT_TEMPLATES, COMMERCE_JD_ROLES, COMMERCE_SKILL_SNIPPETS

# 22 careers → 38 + 22 = 60
EXTRA_CAREERS = [
    ("blockchain-developer", "Blockchain Developer", ["Web Dev", "Cloud/DevOps"], ["Solidity", "Web3.js", "Smart contracts", "Cryptography basics", "Git"], 0.55, 0.72, "medium", 10, "high"),
    ("ar-vr-developer", "AR/VR Developer", ["Game Dev", "Web Dev"], ["Unity", "C#", "3D math", "UX for spatial apps", "Git"], 0.52, 0.75, "medium", 11, "high"),
    ("salesforce-developer", "Salesforce Developer", ["Web Dev", "Business Analyst"], ["Apex", "Lightning", "CRM workflows", "SQL", "Integration APIs"], 0.72, 0.68, "medium", 8, "medium"),
    ("sap-functional-consultant", "SAP Functional Consultant", ["Business Analyst"], ["SAP modules", "Business process", "Requirements", "Testing", "Stakeholder mgmt"], 0.65, 0.55, "medium", 9, "medium"),
    ("digital-marketing-analyst", "Digital Marketing Analyst", ["Business Analyst", "Digital Marketing", "Data Science"], ["Google Analytics", "SQL", "Excel", "A/B testing", "Campaign reporting"], 0.78, 0.62, "medium", 6, "medium"),
    ("growth-marketer-tech", "Growth Marketer (Tech)", ["Web Dev", "Product Management"], ["Funnels", "SQL", "Experimentation", "Copywriting", "Product analytics"], 0.70, 0.70, "medium", 7, "medium"),
    ("supply-chain-analyst", "Supply Chain Analyst", ["Business Analyst", "Data Science"], ["Excel", "SQL", "Forecasting", "Operations research", "Dashboards"], 0.68, 0.65, "medium", 7, "medium"),
    ("hr-tech-analyst", "HR Tech Analyst", ["Business Analyst"], ["HRIS systems", "SQL", "Excel", "People analytics", "Process design"], 0.64, 0.60, "low", 7, "medium"),
    ("fintech-analyst", "FinTech Product Analyst", ["Business Analyst", "Finance & Accounting", "Data Science"], ["SQL", "Payments", "Risk basics", "Regulatory awareness", "Dashboards"], 0.75, 0.78, "medium", 8, "medium"),
    ("quantitative-analyst", "Quantitative Analyst (Junior)", ["Data Science", "Machine Learning"], ["Python", "Statistics", "Time series", "SQL", "Probability"], 0.58, 0.82, "high", 12, "high"),
    ("bi-developer", "BI Developer", ["Data Science", "Business Analyst"], ["Power BI", "SQL", "DAX", "Data modeling", "ETL basics"], 0.80, 0.74, "medium", 7, "medium"),
    ("etl-developer", "ETL Developer", ["Data Science", "Cloud/DevOps"], ["SQL", "Python", "Airflow", "Data modeling", "Cloud storage"], 0.76, 0.80, "medium", 8, "medium"),
    ("release-engineer", "Release Engineer", ["Cloud/DevOps"], ["CI/CD", "Git", "Scripting", "Artifact management", "Release coordination"], 0.72, 0.76, "medium", 8, "medium"),
    ("platform-engineer", "Platform Engineer", ["Cloud/DevOps"], ["Kubernetes", "Terraform", "Python/Go", "Observability", "Internal developer platforms"], 0.74, 0.92, "high", 10, "high"),
    ("api-developer", "API Developer", ["Web Dev"], ["REST", "OpenAPI", "Python or Node", "Auth", "PostgreSQL"], 0.82, 0.84, "medium", 7, "medium"),
    ("developer-advocate", "Developer Advocate", ["Web Dev", "Product Management"], ["Technical writing", "Public speaking", "APIs", "Community building", "Demo apps"], 0.48, 0.78, "medium", 9, "medium"),
    ("scrum-master-tech", "Scrum Master (Tech teams)", ["Product Management"], ["Agile", "Facilitation", "Jira", "Stakeholder communication", "Delivery metrics"], 0.68, 0.58, "medium", 8, "medium"),
    ("it-auditor", "IT Auditor (Tech)", ["Cybersecurity", "Business Analyst"], ["Controls", "Risk", "Compliance", "SQL", "Documentation"], 0.60, 0.62, "medium", 9, "high"),
    ("gis-analyst", "GIS Analyst", ["Data Science"], ["QGIS/ArcGIS", "Python", "Spatial SQL", "Remote sensing basics", "Visualization"], 0.50, 0.68, "low", 9, "medium"),
    ("bioinformatics-analyst", "Bioinformatics Analyst", ["Data Science", "Machine Learning"], ["Python", "R", "Genomics basics", "Statistics", "Linux"], 0.48, 0.88, "medium", 11, "high"),
    ("aerospace-software-engineer", "Aerospace Software Engineer", ["Hardware", "Robotics"], ["C++", "MATLAB", "RTOS", "Simulation", "DO-178 awareness"], 0.45, 0.80, "medium", 12, "high"),
    ("automotive-embedded-engineer", "Automotive Embedded Engineer", ["Hardware", "Robotics"], ["C", "AUTOSAR basics", "CAN bus", "Embedded Linux", "Testing"], 0.58, 0.76, "medium", 11, "high"),
]

EXTRA_RISK: dict[str, tuple] = {
    "blockchain-developer": (2, ["Copy-paste smart contracts"], ["Protocol design", "Security review"], "Web3 Protocol Engineer", ["Solidity security", "Economics"]),
    "ar-vr-developer": (2, ["Asset store assembly"], ["Spatial UX", "Performance"], "Immersive Experience Engineer", ["3D optimization", "Interaction design"]),
    "salesforce-developer": (2, ["Config-only admin tasks"], ["Integration architecture", "Apex depth"], "Salesforce Solution Architect", ["CRM strategy", "Governance"]),
    "sap-functional-consultant": (2, ["Manual test scripts"], ["Process redesign", "Change mgmt"], "SAP Transformation Lead", ["Domain expertise", "Stakeholder influence"]),
    "digital-marketing-analyst": (2, ["Report formatting"], ["Attribution modeling", "Experiment design"], "Growth Analytics Lead", ["SQL", "Storytelling"]),
    "growth-marketer-tech": (2, ["Vanity metrics slides"], ["Funnel optimization", "Product-led growth"], "Head of Growth", ["Experimentation", "Analytics"]),
    "supply-chain-analyst": (2, ["Spreadsheet busywork"], ["Forecast accuracy", "Network design"], "Supply Chain Strategist", ["Operations", "SQL"]),
    "hr-tech-analyst": (2, ["Manual HR reports"], ["People analytics", "Workforce planning"], "HR Analytics Lead", ["HRIS", "Privacy awareness"]),
    "fintech-analyst": (2, ["Basic reconciliation"], ["Risk modeling", "Product insight"], "FinTech Product Strategist", ["Payments", "Compliance"]),
    "quantitative-analyst": (1, ["Spreadsheet models only"], ["Statistical rigor", "Backtesting"], "Quant Researcher", ["Python", "Probability"]),
    "bi-developer": (2, ["Static dashboard dumps"], ["Semantic models", "Self-serve BI"], "Analytics Engineering Lead", ["DAX", "Data modeling"]),
    "etl-developer": (1, ["Hand-written SQL scripts"], ["Pipeline reliability", "Data quality"], "Data Platform Engineer", ["Airflow", "dbt"]),
    "release-engineer": (2, ["Manual release checklists"], ["Pipeline automation", "Release governance"], "DevOps Lead", ["CI/CD", "Change management"]),
    "platform-engineer": (1, ["Ticket-driven kubectl"], ["Platform APIs", "Golden paths"], "Internal Platform Architect", ["K8s", "Developer experience"]),
    "api-developer": (2, ["CRUD boilerplate"], ["API design", "Versioning"], "API Platform Engineer", ["Auth", "Observability"]),
    "developer-advocate": (1, ["Generic blog posts"], ["Technical storytelling", "Community trust"], "Head of Developer Relations", ["Demos", "Feedback loops"]),
    "scrum-master-tech": (2, ["Status meeting notes"], ["Delivery unblock", "Team health"], "Agile Coach", ["Facilitation", "Metrics"]),
    "it-auditor": (2, ["Checkbox audits"], ["Risk assessment", "Control design"], "GRC Lead", ["Compliance", "Security"]),
    "gis-analyst": (2, ["Map styling only"], ["Spatial analysis", "Modeling"], "Geospatial Data Scientist", ["Python", "Remote sensing"]),
    "bioinformatics-analyst": (1, ["Pipeline script copying"], ["Research rigor", "Reproducibility"], "Computational Biologist", ["Stats", "Domain biology"]),
    "aerospace-software-engineer": (2, ["Documentation busywork"], ["Safety-critical coding", "Verification"], "Avionics Software Engineer", ["RTOS", "Standards"]),
    "automotive-embedded-engineer": (2, ["Basic ECU configs"], ["AUTOSAR integration", "Validation"], "Automotive Software Architect", ["C", "Functional safety basics"]),
}

JD_COUNT = 50

JD_ROLES = [
    "data-analyst",
    "data-scientist",
    "ml-engineer",
    "full-stack-developer",
    "frontend-developer",
    "backend-developer",
    "devops-engineer",
    "mobile-developer",
    "ui-ux-designer",
    "cybersecurity-analyst",
    "analytics-engineer",
    "data-engineer",
    "cloud-engineer",
    "business-analyst-tech",
    "qa-automation-engineer",
    "product-manager-tech",
    "nlp-engineer",
    "solutions-engineer",
    "bi-developer",
    "platform-engineer",
] + COMMERCE_JD_ROLES

EXTRA_COMPANIES = [
    "Razorpay", "Swiggy", "Flipkart", "Zoho", "Freshworks", "PhonePe", "CRED", "Meesho",
    "Groww", "Postman", "Paytm", "Ola", "Zomato", "Nykaa", "ShareChat", "Dream11",
    "Lenskart", "Delhivery", "Udaan", "Policybazaar", "Rivigo", "BrowserStack",
    "Chargebee", "CleverTap", "Druva", "ElasticRun", "Eruditus", "Games24x7",
    "Gupshup", "HackerRank", "InMobi", "Juspay", "Licious", "Mamaearth", "Mindtickle",
    "Moglix", "Navi", "OfBusiness", "Porter", "Practo", "Purplle", "Rapido",
    "Slice", "Spinny", "Tata 1mg", "Unacademy", "Vedantu", "Wakefit", "Whatfix",
    "Yubi", "Zepto",
]

EXTRA_SKILL_SNIPPETS: dict[str, list[str]] = {
    "analytics-engineer": ["SQL", "dbt", "Python", "Data modeling", "Airflow", "Git"],
    "data-engineer": ["Python", "Spark", "SQL", "Airflow", "AWS", "Data modeling"],
    "cloud-engineer": ["AWS", "Azure", "Terraform", "Networking", "Linux", "Security"],
    "business-analyst-tech": ["SQL", "Excel", "Requirements", "Jira", "Process mapping", "Stakeholder communication"],
    "qa-automation-engineer": ["Selenium", "Playwright", "Python", "API testing", "CI/CD", "Test strategy"],
    "product-manager-tech": ["Roadmapping", "SQL", "User research", "Agile", "Metrics", "Communication"],
    "nlp-engineer": ["Python", "Transformers", "NLP", "RAG", "Evaluation", "MLOps basics"],
    "solutions-engineer": ["APIs", "SQL", "Presentation", "POC building", "Debugging", "CRM tools"],
    "bi-developer": ["Power BI", "SQL", "DAX", "ETL", "Data modeling", "Excel"],
    "platform-engineer": ["Kubernetes", "Terraform", "Python", "CI/CD", "Observability", "Linux"],
}

ROLE_CERT_TEMPLATES: dict[str, list[tuple[str, float]]] = {
    "data-analyst": [
        ("Google Data Analytics Professional Certificate", 0.80),
        ("Microsoft Power BI Data Analyst", 0.60),
        ("IBM Data Analyst Professional Certificate", 0.30),
    ],
    "data-scientist": [
        ("IBM Data Science Professional Certificate", 0.70),
        ("Google Advanced Data Analytics Certificate", 0.50),
    ],
    "ml-engineer": [
        ("Google Professional Machine Learning Engineer", 0.60),
        ("TensorFlow Developer Certificate", 0.40),
        ("AWS Certified Machine Learning – Specialty", 0.30),
    ],
    "full-stack-developer": [
        ("AWS Certified Cloud Practitioner", 0.60),
        ("Meta Front-End Developer Professional Certificate", 0.40),
    ],
    "frontend-developer": [
        ("Meta Front-End Developer Professional Certificate", 0.80),
        ("Google UX Design Professional Certificate", 0.30),
    ],
    "backend-developer": [
        ("AWS Certified Cloud Practitioner", 0.70),
        ("Oracle Java SE Associate", 0.40),
    ],
    "devops-engineer": [
        ("AWS Certified Cloud Practitioner", 0.80),
        ("CKA: Certified Kubernetes Administrator", 0.40),
        ("HashiCorp Terraform Associate", 0.30),
    ],
    "ui-ux-designer": [
        ("Google UX Design Professional Certificate", 0.80),
        ("NN/g UX Certification", 0.30),
    ],
    "cybersecurity-analyst": [
        ("CompTIA Security+", 0.70),
        ("Google Cybersecurity Professional Certificate", 0.50),
    ],
    "mobile-developer": [
        ("Google Associate Android Developer", 0.60),
        ("Meta Android Developer Professional Certificate", 0.40),
    ],
    "analytics-engineer": [
        ("dbt Analytics Engineering Certification", 0.50),
        ("Google Data Analytics Professional Certificate", 0.40),
    ],
    "data-engineer": [
        ("AWS Certified Cloud Practitioner", 0.70),
        ("Databricks Lakehouse Fundamentals", 0.40),
    ],
    "cloud-engineer": [
        ("AWS Certified Cloud Practitioner", 0.80),
        ("Azure Fundamentals AZ-900", 0.50),
    ],
    "business-analyst-tech": [
        ("Google Data Analytics Professional Certificate", 0.40),
        ("IIBA ECBA (entry BA)", 0.30),
    ],
    "qa-automation-engineer": [
        ("ISTQB Foundation Level", 0.40),
        ("AWS Certified Cloud Practitioner", 0.30),
    ],
    "product-manager-tech": [
        ("Product School certificates", 0.30),
        ("Google Data Analytics Professional Certificate", 0.30),
    ],
    "nlp-engineer": [
        ("TensorFlow Developer Certificate", 0.40),
        ("Google Professional Machine Learning Engineer", 0.40),
    ],
    "solutions-engineer": [
        ("AWS Certified Cloud Practitioner", 0.50),
        ("Salesforce Administrator", 0.30),
    ],
    "bi-developer": [
        ("Microsoft Power BI Data Analyst", 0.70),
        ("Google Data Analytics Professional Certificate", 0.40),
    ],
    "platform-engineer": [
        ("CKA: Certified Kubernetes Administrator", 0.50),
        ("AWS Certified Cloud Practitioner", 0.60),
    ],
    **COMMERCE_CERT_TEMPLATES,
}


def cert_indices_for_role(role: str, jd_count: int) -> list[tuple[str, list[int]]]:
    """Build cert -> JD index lists from target mention percentages."""
    templates = ROLE_CERT_TEMPLATES.get(role, [
        ("AWS Certified Cloud Practitioner", 0.40),
        ("Industry fundamentals certificate", 0.25),
    ])
    result: list[tuple[str, list[int]]] = []
    for cert_name, pct in templates:
        n = max(1, round(jd_count * pct))
        indices = list(range(min(n, jd_count)))
        result.append((cert_name, indices))
    return result


def merge_skill_snippets(base: dict[str, list[str]]) -> dict[str, list[str]]:
    merged = dict(base)
    merged.update(EXTRA_SKILL_SNIPPETS)
    merged.update(COMMERCE_SKILL_SNIPPETS)
    return merged
