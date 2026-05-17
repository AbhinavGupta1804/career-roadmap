import type { InterestArea } from "@/lib/schemas/intake";

export const YEAR_OPTIONS = [
  "1st",
  "2nd",
  "3rd",
  "4th",
  "Dropout",
  "Gap year",
] as const;

export const STREAM_OPTIONS = ["CS", "IT", "ECE", "EE"] as const;

export const COLLEGE_TIER_OPTIONS = [
  "Tier 1 (IIT/NIT/IIIT)",
  "Tier 2",
  "Tier 3",
] as const;

export const CGPA_OPTIONS = ["<6.5", "6.5–7.5", "7.5–8.5", "8.5+"] as const;

export const RELOCATION_OPTIONS = ["Yes", "No", "Open to remote"] as const;

export const HOURS_OPTIONS = ["1hr", "2–3hr", "4+hr"] as const;

export const BUDGET_OPTIONS = ["0", "0–2k", "2–10k", "10k+"] as const;

export const INTEREST_OPTIONS: InterestArea[] = [
  "Machine Learning",
  "Data Science",
  "UI/UX Design",
  "Web Dev",
  "Mobile Dev",
  "Cybersecurity",
  "Cloud/DevOps",
  "Product Management",
  "Game Dev",
  "Hardware",
  "Robotics",
  "Business Analyst",
  "Other",
];

export const SKILL_RATING_OPTIONS = [
  "heard of it",
  "can use with help",
  "can build solo",
] as const;

export const COMMON_SKILLS = [
  "Python",
  "Java",
  "JavaScript",
  "TypeScript",
  "C/C++",
  "SQL",
  "HTML/CSS",
  "React",
  "Node.js",
  "Git",
  "Figma",
  "Excel",
  "AWS",
  "Docker",
  "Kotlin",
  "Swift",
  "R",
  "MATLAB",
  "TensorFlow/PyTorch",
  "Linux",
] as const;

export const GOAL_OPTIONS = [
  "First job",
  "Internship",
  "Higher studies",
  "Startup",
  "Freelancing",
] as const;

export const SALARY_OPTIONS = ["₹3–6 LPA", "₹6–12 LPA", "₹12+ LPA"] as const;

export const TIMELINE_OPTIONS = [
  "3 months",
  "6 months",
  "12 months",
  "2+ years",
] as const;

export const LIKERT_LABELS = [
  { key: "coding_comfort" as const, label: "Coding comfort" },
  { key: "math_logic_comfort" as const, label: "Math / logic comfort" },
  { key: "communication_comfort" as const, label: "Communication / English" },
  { key: "design_visual_comfort" as const, label: "Design / visual thinking" },
  { key: "people_sales_comfort" as const, label: "People / sales / persuasion" },
  { key: "detail_patience" as const, label: "Patience for detail-heavy work" },
];

export const DRAFT_STORAGE_KEY = "career-roadmap-intake-draft";
