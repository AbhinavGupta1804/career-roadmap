import type {
  IntakeForm,
  ProfileBasics,
  SelfAssessment,
  SkillsAndGoals,
} from "@/lib/schemas/intake";
import { DRAFT_STORAGE_KEY } from "@/lib/intake-constants";

export type IntakeStep = 1 | 2 | 3;

export type IntakeDraft = {
  step: IntakeStep;
  profile: Partial<ProfileBasics>;
  self_assessment: Partial<SelfAssessment>;
  skills_and_goals: Partial<SkillsAndGoals> & {
    dream_companies?: string[];
  };
};

export const defaultDraft = (): IntakeDraft => ({
  step: 1,
  profile: {},
  self_assessment: {
    coding_comfort: 3,
    math_logic_comfort: 3,
    communication_comfort: 3,
    design_visual_comfort: 3,
    people_sales_comfort: 3,
    detail_patience: 3,
    interest_bias: [],
    commitment_slider: 5,
  },
  skills_and_goals: {
    skills: [],
    has_internship: false,
    dream_companies: [],
  },
});

export function loadDraft(): IntakeDraft {
  if (typeof window === "undefined") return defaultDraft();
  try {
    const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (!raw) return defaultDraft();
    return { ...defaultDraft(), ...JSON.parse(raw) } as IntakeDraft;
  } catch {
    return defaultDraft();
  }
}

export function saveDraft(draft: IntakeDraft) {
  localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft));
}

export function clearDraft() {
  localStorage.removeItem(DRAFT_STORAGE_KEY);
}

export function draftToIntakeForm(draft: IntakeDraft): IntakeForm {
  return {
    profile: draft.profile as ProfileBasics,
    self_assessment: draft.self_assessment as SelfAssessment,
    skills_and_goals: {
      skills: draft.skills_and_goals.skills ?? [],
      projects_text: draft.skills_and_goals.projects_text?.trim() || null,
      github_url: draft.skills_and_goals.github_url?.trim() || undefined,
      has_internship: draft.skills_and_goals.has_internship ?? false,
      internship_brief: draft.skills_and_goals.internship_brief?.trim() || null,
      primary_goal: draft.skills_and_goals.primary_goal!,
      target_salary_band: draft.skills_and_goals.target_salary_band!,
      timeline_to_job: draft.skills_and_goals.timeline_to_job!,
      dream_companies: (draft.skills_and_goals.dream_companies ?? []).filter(
        Boolean,
      ),
    },
  };
}
