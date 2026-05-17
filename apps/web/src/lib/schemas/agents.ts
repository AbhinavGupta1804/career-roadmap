import { z } from "zod";

export const trackTypeSchema = z.enum(["Stretch", "Realistic", "Safe"]);
export const aiRiskTierSchema = z.union([
  z.literal(1),
  z.literal(2),
  z.literal(3),
  z.literal(4),
  z.literal(5),
]);

export const careerTrackSchema = z.object({
  name: z.string(),
  career_slug: z.string(),
  type: trackTypeSchema,
  why_recommended: z.string(),
  avg_starting_salary_band: z.string(),
  time_to_job_estimate_months: z.number().int().min(1).max(36),
  competition_level: z.enum(["low", "medium", "high"]),
  top_hiring_companies: z.array(z.string()).max(8).default([]),
  honest_warning: z.string().nullable().optional(),
  ai_risk_tier: aiRiskTierSchema.nullable().optional(),
  ai_risk_label: z.string().nullable().optional(),
  replaces: z.array(z.string()).default([]),
  amplifies: z.array(z.string()).default([]),
  evolved_role_2029: z.string().nullable().optional(),
  survival_skills: z.array(z.string()).default([]),
});

export const careerPathPickerOutputSchema = z.object({
  tracks: z.tuple([
    careerTrackSchema,
    careerTrackSchema,
    careerTrackSchema,
  ]),
});

export const disruptionBriefingSchema = z.object({
  summary: z.string(),
  rejected_paths: z.array(z.string()).default([]),
  do_not_pursue_callouts: z.array(z.string()).default([]),
});

export const aiRealityCheckOutputSchema = z.object({
  tracks: z.tuple([
    careerTrackSchema,
    careerTrackSchema,
    careerTrackSchema,
  ]),
  disruption_briefing: disruptionBriefingSchema,
});

export const skillGapItemSchema = z.object({
  name: z.string(),
  current_level: z.number().int().min(0).max(5),
  required_level: z.number().int().min(1).max(5),
  demand_frequency_pct: z.number().min(0).max(100),
  weeks_to_bridge: z.number().int().min(0).max(52),
  priority: z.enum(["must", "should", "nice"]),
});

export const skillGapAnalyzerOutputSchema = z.object({
  role: z.string(),
  career_slug: z.string(),
  skills: z.array(skillGapItemSchema),
});

export const learningWeekSchema = z.object({
  week: z.number().int().min(1),
  focus_skill: z.string(),
  resources: z.array(z.string()),
  hours: z.number().int().min(1),
  mini_task: z.string(),
  checkpoint: z.boolean().default(false),
});

export const learningPathGeneratorOutputSchema = z.object({
  total_weeks: z.number().int().min(1),
  weeks: z.array(learningWeekSchema),
});

export const portfolioProjectSchema = z.object({
  name: z.string(),
  difficulty: z.enum([
    "Beginner",
    "Easy",
    "Medium",
    "Hard",
    "Capstone",
  ]),
  problem_statement: z.string(),
  dataset_or_api: z.string().nullable().optional(),
  expected_output: z.string(),
  hours_estimate: z.number().int().min(4),
  tech_stack: z.array(z.string()),
  resume_bullet: z.string(),
});

export const projectIdeatorOutputSchema = z.object({
  projects: z
    .tuple([
      portfolioProjectSchema,
      portfolioProjectSchema,
      portfolioProjectSchema,
      portfolioProjectSchema,
      portfolioProjectSchema,
    ])
    .or(z.array(portfolioProjectSchema).length(5)),
});

export const certificationItemSchema = z.object({
  name: z.string(),
  provider: z.string(),
  cost: z.string(),
  hours: z.number().int(),
  why: z.string(),
});

export const certificationAdvisorOutputSchema = z.object({
  recommended: z.array(certificationItemSchema),
  skip: z.array(
    z.object({
      name: z.string(),
      why_skip: z.string(),
    }),
  ),
});

export const portfolioBuilderOutputSchema = z.object({
  github_readme_md: z.string(),
  portfolio_site_sections: z.array(
    z.object({
      section: z.enum(["hero", "about", "projects", "skills", "contact"]),
      content: z.string(),
    }),
  ),
  hosting_suggestion: z.string(),
  linkedin_calendar: z.array(
    z.object({
      week: z.number().int(),
      post_type: z.enum(["project", "learning", "opinion", "resource"]),
      template: z.string(),
    }),
  ),
  connection_request_templates: z.array(z.string()).min(5).max(5),
});

export const agentOutputsSchema = z.object({
  career_paths: careerPathPickerOutputSchema.nullable().optional(),
  ai_reality_check: aiRealityCheckOutputSchema.nullable().optional(),
  skill_gap: skillGapAnalyzerOutputSchema.nullable().optional(),
  learning_path: learningPathGeneratorOutputSchema.nullable().optional(),
  projects: projectIdeatorOutputSchema.nullable().optional(),
  certifications: certificationAdvisorOutputSchema.nullable().optional(),
  portfolio: portfolioBuilderOutputSchema.nullable().optional(),
  chosen_track_type: trackTypeSchema.nullable().optional(),
});

export type TrackType = z.infer<typeof trackTypeSchema>;
export type CareerTrack = z.infer<typeof careerTrackSchema>;
export type AiRealityCheckOutput = z.infer<typeof aiRealityCheckOutputSchema>;
export type AgentOutputs = z.infer<typeof agentOutputsSchema>;
export type IntakeFormAgents = AgentOutputs;
