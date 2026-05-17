import { z } from "zod";

export const yearOfStudySchema = z.enum([
  "1st",
  "2nd",
  "3rd",
  "4th",
  "Dropout",
  "Gap year",
]);

export const techStreamSchema = z.enum(["CS", "IT", "ECE", "EE"]);

export const collegeTierSchema = z.enum([
  "Tier 1 (IIT/NIT/IIIT)",
  "Tier 2",
  "Tier 3",
]);

export const cgpaBandSchema = z.enum([
  "<6.5",
  "6.5–7.5",
  "7.5–8.5",
  "8.5+",
]);

export const relocationSchema = z.enum(["Yes", "No", "Open to remote"]);
export const hoursPerDaySchema = z.enum(["1hr", "2–3hr", "4+hr"]);
export const budgetInrSchema = z.enum(["0", "0–2k", "2–10k", "10k+"]);

export const interestAreaSchema = z.enum([
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
]);

export const skillRatingSchema = z.enum([
  "heard of it",
  "can use with help",
  "can build solo",
]);

export const primaryGoalSchema = z.enum([
  "First job",
  "Internship",
  "Higher studies",
  "Startup",
  "Freelancing",
]);

export const targetSalaryBandSchema = z.enum([
  "₹3–6 LPA",
  "₹6–12 LPA",
  "₹12+ LPA",
]);

export const timelineToJobSchema = z.enum([
  "3 months",
  "6 months",
  "12 months",
  "2+ years",
]);

export const likertSchema = z.number().int().min(1).max(5);

export const profileBasicsSchema = z.object({
  year_of_study: yearOfStudySchema,
  stream: techStreamSchema,
  college_tier: collegeTierSchema,
  cgpa_band: cgpaBandSchema,
  city: z.string().min(1).max(100),
  relocation: relocationSchema,
  hours_per_day: hoursPerDaySchema,
  budget_inr: budgetInrSchema,
});

export const selfAssessmentSchema = z
  .object({
    coding_comfort: likertSchema,
    math_logic_comfort: likertSchema,
    communication_comfort: likertSchema,
    design_visual_comfort: likertSchema,
    people_sales_comfort: likertSchema,
    detail_patience: likertSchema,
    interest_bias: z.array(interestAreaSchema).min(1).max(3),
    commitment_slider: z.number().int().min(0).max(10),
  })
  .refine(
    (data) => new Set(data.interest_bias).size === data.interest_bias.length,
    { message: "Pick each interest only once", path: ["interest_bias"] },
  );

export const studentSkillSchema = z.object({
  name: z.string().min(1).max(80),
  rating: skillRatingSchema,
});

const optionalUrl = z.preprocess(
  (v) => (v === "" || v === null || v === undefined ? undefined : v),
  z.string().url().optional(),
);

const optionalText = z.preprocess(
  (v) => (v === "" || v === undefined ? null : v),
  z.string().max(2000).nullable().optional(),
);

export const skillsAndGoalsSchema = z.object({
  skills: z.array(studentSkillSchema).default([]),
  projects_text: optionalText,
  github_url: optionalUrl,
  has_internship: z.boolean(),
  internship_brief: z.preprocess(
    (v) => (v === "" || v === undefined ? null : v),
    z.string().max(500).nullable().optional(),
  ),
  primary_goal: primaryGoalSchema,
  target_salary_band: targetSalaryBandSchema,
  timeline_to_job: timelineToJobSchema,
  dream_companies: z.array(z.string()).max(3).default([]),
});

export const intakeFormSchema = z.object({
  profile: profileBasicsSchema,
  self_assessment: selfAssessmentSchema,
  skills_and_goals: skillsAndGoalsSchema,
});

export type YearOfStudy = z.infer<typeof yearOfStudySchema>;
export type TechStream = z.infer<typeof techStreamSchema>;
export type InterestArea = z.infer<typeof interestAreaSchema>;
export type IntakeForm = z.infer<typeof intakeFormSchema>;
export type ProfileBasics = z.infer<typeof profileBasicsSchema>;
export type SelfAssessment = z.infer<typeof selfAssessmentSchema>;
export type SkillsAndGoals = z.infer<typeof skillsAndGoalsSchema>;
export type StudentSkill = z.infer<typeof studentSkillSchema>;
