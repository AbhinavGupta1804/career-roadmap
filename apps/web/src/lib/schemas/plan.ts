import { z } from "zod";

import { agentOutputsSchema, trackTypeSchema } from "@/lib/schemas/agents";

export const weekProgressSchema = z.object({
  completed_weeks: z.array(z.number().int()).default([]),
  current_streak: z.number().int().default(0),
  longest_streak: z.number().int().default(0),
  last_check_in: z.string().nullable().default(null),
});

export type WeekProgress = z.infer<typeof weekProgressSchema>;

const emptyWeekProgress: WeekProgress = {
  completed_weeks: [],
  current_streak: 0,
  longest_streak: 0,
  last_check_in: null,
};

/** Normalize API/partial progress for React state (always includes last_check_in). */
export function normalizeWeekProgress(
  raw?: z.infer<typeof weekProgressSchema> | null,
): WeekProgress {
  if (!raw) return emptyWeekProgress;
  return {
    completed_weeks: raw.completed_weeks,
    current_streak: raw.current_streak,
    longest_streak: raw.longest_streak,
    last_check_in: raw.last_check_in ?? null,
  };
}

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
