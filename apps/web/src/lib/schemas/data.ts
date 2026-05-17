import { z } from "zod";

export const salaryBandSchema = z.object({
  min_lpa: z.number(),
  max_lpa: z.number(),
});

export const careerEntrySchema = z.object({
  slug: z.string(),
  name: z.string(),
  interest_tags: z.array(z.string()).min(1),
  required_skills: z.array(z.string()).min(1),
  salary_bands: z.object({
    tier_1: salaryBandSchema,
    tier_2: salaryBandSchema,
    tier_3: salaryBandSchema,
  }),
  market_demand_index: z.number().min(0).max(1),
  ai_resilience_index: z.number().min(0).max(1),
  competition_level: z.enum(["low", "medium", "high"]),
  typical_months_to_job: z.number().int().min(3).max(24),
  entry_difficulty: z.enum(["low", "medium", "high"]),
});

export const dataStatusSchema = z.object({
  careers_count: z.number(),
  ai_risk_profiles_count: z.number(),
  resources_count: z.number(),
  jd_roles_count: z.number(),
  jd_total_count: z.number(),
  career_slugs_missing_risk_profile: z.array(z.string()),
  risk_profiles_without_career: z.array(z.string()),
  data_valid: z.boolean(),
});

export type CareerEntry = z.infer<typeof careerEntrySchema>;
export type DataStatus = z.infer<typeof dataStatusSchema>;
