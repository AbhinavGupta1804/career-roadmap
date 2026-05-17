import type { PlanResponse } from "@/lib/schemas/plan";

/** Static preview for /plan/demo — layout QA without API. */
export const DEMO_PLAN: PlanResponse = {
  plan_id: "demo",
  intake_id: "demo-intake",
  status: "completed",
  chosen_track_type: "Realistic",
  llm_cost_inr: 0,
  llm_token_log: [],
  agent_outputs: {
    chosen_track_type: "Realistic",
    ai_reality_check: {
      tracks: [
        {
          name: "Data Analyst",
          career_slug: "data-analyst",
          type: "Realistic",
          why_recommended: "Strong fit for your SQL + interest in data.",
          avg_starting_salary_band: "₹6–12 LPA",
          time_to_job_estimate_months: 6,
          competition_level: "medium",
          top_hiring_companies: ["Razorpay", "Swiggy", "Flipkart"],
          honest_warning: "Tier 2 college — portfolio proof matters.",
          ai_risk_tier: 2,
          ai_risk_label: "Augmented",
          replaces: ["Ad-hoc SQL generation"],
          amplifies: ["Metric definition", "Storytelling"],
          evolved_role_2029: "Analytics Strategist",
          survival_skills: ["Domain knowledge", "Stakeholder influence"],
        },
        {
          name: "Analytics Engineer",
          career_slug: "analytics-engineer",
          type: "Stretch",
          why_recommended: "Stretch if you commit to dbt + modeling.",
          avg_starting_salary_band: "₹8–14 LPA",
          time_to_job_estimate_months: 8,
          competition_level: "high",
          top_hiring_companies: ["Razorpay", "CRED"],
          ai_risk_tier: 1,
          ai_risk_label: "Tailwind",
          replaces: [],
          amplifies: ["Semantic layers"],
          evolved_role_2029: "Data Platform Engineer",
          survival_skills: ["dbt", "Data contracts"],
        },
        {
          name: "Business Analyst (Tech)",
          career_slug: "business-analyst-tech",
          type: "Safe",
          why_recommended: "Lower technical bar, strong hiring volume.",
          avg_starting_salary_band: "₹5–9 LPA",
          time_to_job_estimate_months: 5,
          competition_level: "medium",
          top_hiring_companies: ["Zoho", "Freshworks"],
          ai_risk_tier: 2,
          ai_risk_label: "Augmented",
          replaces: ["Slide formatting"],
          amplifies: ["Requirements clarity"],
          evolved_role_2029: "Product Operations Analyst",
          survival_skills: ["SQL", "Domain expertise"],
        },
      ],
      disruption_briefing: {
        summary:
          "Data analyst roles are augmented, not replaced — employers want analysts who define metrics and communicate insights, not only run queries.",
        rejected_paths: [],
        do_not_pursue_callouts: [
          "Avoid generic content-writing or manual QA-only paths (tier 4–5 disruption).",
        ],
      },
    },
    skill_gap: {
      role: "Data Analyst",
      career_slug: "data-analyst",
      skills: [
        {
          name: "SQL",
          current_level: 2,
          required_level: 4,
          demand_frequency_pct: 100,
          weeks_to_bridge: 6,
          priority: "must",
        },
        {
          name: "Power BI",
          current_level: 0,
          required_level: 4,
          demand_frequency_pct: 100,
          weeks_to_bridge: 9,
          priority: "must",
        },
        {
          name: "Excel",
          current_level: 1,
          required_level: 4,
          demand_frequency_pct: 100,
          weeks_to_bridge: 9,
          priority: "should",
        },
      ],
    },
    learning_path: {
      total_weeks: 12,
      weeks: Array.from({ length: 12 }, (_, i) => ({
        week: i + 1,
        focus_skill: ["Excel", "SQL", "SQL", "Python", "Power BI", "Power BI", "Statistics", "Statistics", "Tableau", "Tableau", "Portfolio & interview prep", "Portfolio & interview prep"][i] ?? "SQL",
        resources: ["SQLBolt (SQLBolt)", "Mode SQL Tutorial (Mode)"],
        hours: 10,
        mini_task: `Week ${i + 1}: complete one module and log learnings.`,
        checkpoint: (i + 1) % 4 === 0 || i === 11,
      })),
    },
    projects: {
      projects: [
        {
          name: "Razorpay-style ops metrics (Excel + SQL)",
          difficulty: "Beginner",
          problem_statement: "Analyze weekly GMV & refund metrics for a fintech ops slice.",
          dataset_or_api: "Synthetic payments CSV",
          expected_output: "Workbook + 3 insights",
          hours_estimate: 12,
          tech_stack: ["Excel", "SQL"],
          resume_bullet: "Replicated fresher DA ops analysis for cross-functional stakeholders.",
        },
        {
          name: "Cohort retention pipeline (Python)",
          difficulty: "Easy",
          problem_statement: "Build a Python pipeline for cohort retention tables.",
          dataset_or_api: "Public e-commerce sample",
          expected_output: "Notebook + CSV exports",
          hours_estimate: 20,
          tech_stack: ["Python", "SQL", "Pandas"],
          resume_bullet: "Built cohort retention pipeline mirroring product analyst JDs.",
        },
        {
          name: "Executive KPI dashboard (Power BI)",
          difficulty: "Medium",
          problem_statement: "Cross-functional KPI dashboard from SQL models.",
          dataset_or_api: "Warehouse schema sample",
          expected_output: "Interactive dashboard",
          hours_estimate: 30,
          tech_stack: ["SQL", "Power BI", "Python"],
          resume_bullet: "Delivered executive KPI dashboard backed by SQL.",
        },
        {
          name: "Experiment readout (Statistics)",
          difficulty: "Hard",
          problem_statement: "A/B experiment analysis for a promo campaign.",
          dataset_or_api: "Simulated experiment logs",
          expected_output: "Readout deck with lift & guardrails",
          hours_estimate: 40,
          tech_stack: ["Python", "SQL", "Statistics"],
          resume_bullet: "Quantified experiment lift for growth readout.",
        },
        {
          name: "Capstone: end-to-end metric layer",
          difficulty: "Capstone",
          problem_statement: "Ingest → SQL → dashboard + hiring narrative.",
          dataset_or_api: "Multi-table fintech dataset",
          expected_output: "GitHub repo + case study",
          hours_estimate: 60,
          tech_stack: ["SQL", "Python", "Power BI", "Excel"],
          resume_bullet: "Capstone DA stack with stakeholder-ready story.",
        },
      ],
    },
    certifications: {
      recommended: [
        {
          name: "Google Data Analytics Professional Certificate",
          provider: "Coursera (Google)",
          cost: "Free (audit) · ~₹2,500 with certificate",
          hours: 180,
          why: "Listed on 80% of Data Analyst JDs in our corpus. Strong brand signal for Indian analytics fresher screens.",
        },
        {
          name: "IBM Data Analyst Professional Certificate",
          provider: "Coursera (IBM)",
          cost: "Free (audit)",
          hours: 120,
          why: "Mentioned in 30% of sampled JDs.",
        },
      ],
      skip: [
        {
          name: "Generic Data Science bootcamp certificate (non-employer-linked)",
          why_skip: "DA JDs ask for SQL/BI — not DS bootcamp brands; use projects instead.",
        },
        {
          name: "Random Udemy completion certificates (no capstone)",
          why_skip: "Recruiters discount non-proctored Udemy badges — portfolio projects matter more.",
        },
      ],
    },
    portfolio: {
      github_readme_md: `### 1. Razorpay-style ops metrics (Excel + SQL) (Beginner)
Analyze weekly GMV & refund metrics for a fintech ops slice.

- **Stack:** Excel, SQL
- **Output:** Workbook + 3 insights
- **Data/API:** Synthetic payments CSV
- **Resume:** Replicated fresher DA ops analysis for cross-functional stakeholders.

### 2. Cohort retention pipeline (Python) (Easy)
Build a Python pipeline for cohort retention tables.

- **Stack:** Python, SQL, Pandas
- **Output:** Notebook + CSV exports
- **Data/API:** Public e-commerce sample
- **Resume:** Built cohort retention pipeline mirroring product analyst JDs.

### 3. Executive KPI dashboard (Power BI) (Medium)
Cross-functional KPI dashboard from SQL models.

- **Stack:** SQL, Power BI, Python
- **Output:** Interactive dashboard
- **Data/API:** Warehouse schema sample
- **Resume:** Delivered executive KPI dashboard backed by SQL.

### 4. Experiment readout (Statistics) (Hard)
A/B experiment analysis for a promo campaign.

- **Stack:** Python, SQL, Statistics
- **Output:** Readout deck with lift & guardrails
- **Data/API:** Simulated experiment logs
- **Resume:** Quantified experiment lift for growth readout.

### 5. Capstone: end-to-end metric layer (Capstone)
Ingest → SQL → dashboard + hiring narrative.

- **Stack:** SQL, Python, Power BI, Excel
- **Output:** GitHub repo + case study
- **Data/API:** Multi-table fintech dataset
- **Resume:** Capstone DA stack with stakeholder-ready story.`,
      portfolio_site_sections: [
        {
          section: "hero",
          content:
            "Hi, I'm a 3rd-year CS student from Pune targeting Data Analyst roles (₹6–12 LPA).",
        },
        {
          section: "about",
          content:
            "Focused on Data Analyst · Tier 2 · CGPA 7.5–8.5 · Dream companies: Razorpay, Swiggy.",
        },
        {
          section: "projects",
          content:
            "**Cross-functional KPI dashboard** (Beginner) — SQL + Excel metrics for growth teams.",
        },
        {
          section: "skills",
          content: "**SQL** — 2/5 → 4/5 (must) · **Power BI** — 2/5 → 4/5 (must)",
        },
        {
          section: "contact",
          content: "📍 Pune · LinkedIn: [your-profile] · GitHub: [your-username]",
        },
      ],
      hosting_suggestion:
        "**GitHub Pages** (free) — publish case studies; embed Power BI Public dashboards.",
      linkedin_calendar: [
        { week: 1, post_type: "learning", template: "Week 1 · Learning update — focused on SQL." },
        { week: 1, post_type: "project", template: "Week 1 · Showcasing KPI dashboard WIP." },
        { week: 1, post_type: "opinion", template: "Week 1 · Dashboards don't get you hired — decisions do." },
        { week: 1, post_type: "resource", template: "Week 1 · SQLBolt helped my joins practice." },
        { week: 2, post_type: "learning", template: "Week 2 · Deep dive on Power BI DAX." },
        { week: 2, post_type: "project", template: "Week 2 · Demo GIF of dashboard v1." },
        { week: 2, post_type: "opinion", template: "Week 2 · Tier-2 grads win with narrative + metrics." },
        { week: 2, post_type: "resource", template: "Week 2 · Microsoft Learn Power BI path." },
      ],
      connection_request_templates: [
        "Hi [Name], I'm a 3rd-year CS student targeting Data Analyst roles — open to a 15-min chat?",
        "Hi [Name], fellow Pune-based grad building a DA portfolio — what do hiring managers look for?",
        "Hi [Name], I admire Razorpay's data culture — one question on portfolio reviews?",
        "Hi [Name], I'm documenting weekly builds on LinkedIn — would love to connect.",
        "Hi [Name], I shipped my first dashboard milestone — feedback on job-ready signal?",
      ],
    },
  },
};
