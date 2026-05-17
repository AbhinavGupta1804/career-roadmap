import { z } from "zod";

import { agentOutputsSchema, trackTypeSchema } from "@/lib/schemas/agents";

export const weekProgressSchema = z.object({
  completed_weeks: z.array(z.number().int()).default([]),
  current_streak: z.number().int().default(0),
  longest_streak: z.number().int().default(0),
  last_check_in: z.string().nullable().optional(),
});

export const planResponseSchema = z.object({
  plan_id: z.string(),
  intake_id: z.string(),
  status: z.string(),
  chosen_track_type: trackTypeSchema.nullable().optional(),
  agent_outputs: agentOutputsSchema.default({}),
  week_progress: weekProgressSchema.optional(),
  llm_cost_inr: z.number().default(0),
  llm_token_log: z.array(z.record(z.string(), z.unknown())).default([]),
});

export type PlanResponse = z.infer<typeof planResponseSchema>;
