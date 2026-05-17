"use client";

import { INTEREST_OPTIONS, LIKERT_LABELS } from "@/lib/intake-constants";
import type { InterestArea, SelfAssessment } from "@/lib/schemas/intake";
import { Field } from "@/components/intake/form-primitives";

type Props = {
  value: Partial<SelfAssessment>;
  errors: Record<string, string>;
  onChange: (patch: Partial<SelfAssessment>) => void;
};

export function StepAssessment({ value, errors, onChange }: Props) {
  const ranked = value.interest_bias ?? [];

  function toggleInterest(area: InterestArea) {
    if (ranked.includes(area)) {
      onChange({ interest_bias: ranked.filter((x) => x !== area) });
      return;
    }
    if (ranked.length >= 3) return;
    onChange({ interest_bias: [...ranked, area] });
  }

  return (
    <div className="space-y-6">
      <p className="text-sm text-zinc-600 dark:text-zinc-400">
        Rate yourself 1 (low) to 5 (high). Be honest — this shapes your roadmap.
      </p>

      {LIKERT_LABELS.map(({ key, label }) => (
        <Field key={key} label={label}>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => onChange({ [key]: n })}
                className={`flex h-11 w-11 items-center justify-center rounded-lg border text-sm font-medium transition ${
                  value[key] === n
                    ? "border-violet-600 bg-violet-600 text-white"
                    : "border-zinc-200 text-zinc-700 hover:border-violet-300 dark:border-zinc-700 dark:text-zinc-300"
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </Field>
      ))}

      <Field
        label="Interest bias"
        hint="Pick up to 3 areas you're drawn to. Tap in order of preference (1st, 2nd, 3rd)."
        error={errors.interest_bias}
      >
        <div className="flex flex-wrap gap-2">
          {INTEREST_OPTIONS.map((area) => {
            const rank = ranked.indexOf(area);
            const selected = rank >= 0;
            return (
              <button
                key={area}
                type="button"
                onClick={() => toggleInterest(area)}
                className={`min-h-[40px] rounded-full border px-3 py-1.5 text-sm transition ${
                  selected
                    ? "border-violet-600 bg-violet-600 text-white"
                    : "border-zinc-200 text-zinc-700 hover:border-violet-300 dark:border-zinc-700 dark:text-zinc-300"
                }`}
              >
                {selected ? `#${rank + 1} ` : ""}
                {area}
              </button>
            );
          })}
        </div>
      </Field>

      <Field
        label="Commitment to chosen interests"
        hint="0 = open to surprises · 10 = stay strictly on these interests"
        error={errors.commitment_slider}
      >
        <div className="space-y-2">
          <input
            type="range"
            min={0}
            max={10}
            value={value.commitment_slider ?? 5}
            onChange={(e) =>
              onChange({ commitment_slider: Number(e.target.value) })
            }
            className="w-full accent-violet-600"
          />
          <div className="flex justify-between text-xs text-zinc-500">
            <span>Open to surprises</span>
            <span className="font-medium text-violet-600">
              {value.commitment_slider ?? 5}
            </span>
            <span>Very committed</span>
          </div>
        </div>
      </Field>
    </div>
  );
}
