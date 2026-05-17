"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ZodError } from "zod";

import { StepAssessment } from "@/components/intake/step-assessment";
import { StepProfile } from "@/components/intake/step-profile";
import { StepSkills } from "@/components/intake/step-skills";
import { startPlan, submitIntake } from "@/lib/api";
import {
  clearDraft,
  defaultDraft,
  draftToIntakeForm,
  loadDraft,
  saveDraft,
  type IntakeDraft,
} from "@/lib/intake-draft";
import {
  intakeFormSchema,
  profileBasicsSchema,
  selfAssessmentSchema,
} from "@/lib/schemas/intake";

const STEPS = [
  { n: 1 as const, title: "Profile" },
  { n: 2 as const, title: "Self-assessment" },
  { n: 3 as const, title: "Skills & goals" },
];

function zodFieldErrors(error: ZodError): Record<string, string> {
  const out: Record<string, string> = {};
  for (const issue of error.issues) {
    const key = issue.path.join(".") || "_form";
    if (!out[key]) out[key] = issue.message;
  }
  return out;
}

export function IntakeWizard() {
  const router = useRouter();
  const [draft, setDraft] = useState<IntakeDraft>(defaultDraft);
  const [hydrated, setHydrated] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(loadDraft());
    setHydrated(true);
  }, []);

  const persist = useCallback((next: IntakeDraft) => {
    setDraft(next);
    saveDraft(next);
  }, []);

  function validateStep(step: 1 | 2 | 3): boolean {
    try {
      if (step === 1) {
        profileBasicsSchema.parse(draft.profile);
      } else if (step === 2) {
        selfAssessmentSchema.parse(draft.self_assessment);
      } else {
        intakeFormSchema.parse(draftToIntakeForm(draft));
      }
      setErrors({});
      return true;
    } catch (e) {
      if (e instanceof ZodError) {
        setErrors(zodFieldErrors(e));
      }
      return false;
    }
  }

  function goNext() {
    if (!validateStep(draft.step)) return;
    if (draft.step < 3) {
      persist({ ...draft, step: (draft.step + 1) as 1 | 2 | 3 });
    }
  }

  function goBack() {
    if (draft.step > 1) {
      persist({ ...draft, step: (draft.step - 1) as 1 | 2 | 3 });
      setErrors({});
    }
  }

  async function handleSubmit() {
    if (!validateStep(3)) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const form = intakeFormSchema.parse(draftToIntakeForm(draft));
      const created = await submitIntake(form);
      const plan = await startPlan(created.submission_id);
      clearDraft();
      router.push(`/plan/${plan.plan_id}`);
    } catch (e) {
      setSubmitError(
        e instanceof Error ? e.message : "Failed to submit. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!hydrated) {
    return (
      <p className="text-center text-sm text-zinc-500">Loading draft…</p>
    );
  }

  const progress = (draft.step / 3) * 100;

  return (
    <div className="space-y-6">
      <div>
        <div className="mb-2 flex justify-between text-xs font-medium text-zinc-500">
          <span>
            Step {draft.step} of 3 — {STEPS[draft.step - 1].title}
          </span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
          <div
            className="h-full rounded-full bg-violet-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-2 text-xs text-zinc-500">
          Draft auto-saved on this device
        </p>
      </div>

      {draft.step === 1 ? (
        <StepProfile
          value={draft.profile}
          errors={errors}
          onChange={(patch) =>
            persist({ ...draft, profile: { ...draft.profile, ...patch } })
          }
        />
      ) : null}

      {draft.step === 2 ? (
        <StepAssessment
          value={draft.self_assessment}
          errors={errors}
          onChange={(patch) =>
            persist({
              ...draft,
              self_assessment: { ...draft.self_assessment, ...patch },
            })
          }
        />
      ) : null}

      {draft.step === 3 ? (
        <StepSkills
          value={draft.skills_and_goals}
          errors={errors}
          onChange={(patch) =>
            persist({
              ...draft,
              skills_and_goals: { ...draft.skills_and_goals, ...patch },
            })
          }
        />
      ) : null}

      {submitError ? (
        <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
          {submitError}
        </p>
      ) : null}

      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-between">
        <button
          type="button"
          onClick={goBack}
          disabled={draft.step === 1 || submitting}
          className="inline-flex h-11 items-center justify-center rounded-full border border-zinc-300 px-6 text-sm font-medium text-zinc-700 disabled:opacity-40 dark:border-zinc-700 dark:text-zinc-300"
        >
          Back
        </button>
        {draft.step < 3 ? (
          <button
            type="button"
            onClick={goNext}
            className="inline-flex h-11 items-center justify-center rounded-full bg-violet-600 px-8 text-sm font-medium text-white hover:bg-violet-500"
          >
            Continue
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting}
            className="inline-flex h-11 items-center justify-center rounded-full bg-violet-600 px-8 text-sm font-medium text-white hover:bg-violet-500 disabled:opacity-60"
          >
            {submitting ? "Building your roadmap…" : "Generate my mission plan"}
          </button>
        )}
      </div>
    </div>
  );
}
