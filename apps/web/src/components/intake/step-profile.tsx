"use client";

import {
  BUDGET_OPTIONS,
  CGPA_OPTIONS,
  COLLEGE_TIER_OPTIONS,
  HOURS_OPTIONS,
  RELOCATION_OPTIONS,
  BRANCH_OPTIONS,
  YEAR_OPTIONS,
} from "@/lib/intake-constants";
import type { ProfileBasics } from "@/lib/schemas/intake";
import {
  Field,
  RadioGroup,
  SelectInput,
  TextInput,
} from "@/components/intake/form-primitives";

type Props = {
  value: Partial<ProfileBasics>;
  errors: Record<string, string>;
  onChange: (patch: Partial<ProfileBasics>) => void;
};

export function StepProfile({ value, errors, onChange }: Props) {
  return (
    <div className="space-y-5">
      <Field label="Year of study" error={errors.year_of_study}>
        <SelectInput
          value={value.year_of_study ?? ""}
          onChange={(e) =>
            onChange({
              year_of_study: e.target.value as ProfileBasics["year_of_study"],
            })
          }
        >
          <option value="">Select year</option>
          {YEAR_OPTIONS.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </SelectInput>
      </Field>

      <Field label="Branch / degree" error={errors.stream}>
        <SelectInput
          value={value.stream ?? ""}
          onChange={(e) =>
            onChange({ stream: e.target.value as ProfileBasics["stream"] })
          }
        >
          <option value="">Select branch</option>
          {BRANCH_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </SelectInput>
      </Field>

      <Field label="College tier" error={errors.college_tier}>
        <RadioGroup
          name="college_tier"
          value={value.college_tier}
          options={COLLEGE_TIER_OPTIONS}
          onChange={(college_tier) => onChange({ college_tier })}
        />
      </Field>

      <Field label="CGPA band" error={errors.cgpa_band}>
        <RadioGroup
          name="cgpa_band"
          value={value.cgpa_band}
          options={CGPA_OPTIONS}
          onChange={(cgpa_band) => onChange({ cgpa_band })}
        />
      </Field>

      <Field label="City" error={errors.city}>
        <TextInput
          placeholder="e.g. Pune"
          value={value.city ?? ""}
          onChange={(e) => onChange({ city: e.target.value })}
        />
      </Field>

      <Field label="Open to relocation?" error={errors.relocation}>
        <RadioGroup
          name="relocation"
          value={value.relocation}
          options={RELOCATION_OPTIONS}
          onChange={(relocation) => onChange({ relocation })}
        />
      </Field>

      <Field
        label="Hours per day for upskilling"
        error={errors.hours_per_day}
      >
        <RadioGroup
          name="hours_per_day"
          value={value.hours_per_day}
          options={HOURS_OPTIONS}
          onChange={(hours_per_day) => onChange({ hours_per_day })}
        />
      </Field>

      <Field label="Budget for courses (₹)" error={errors.budget_inr}>
        <RadioGroup
          name="budget_inr"
          value={value.budget_inr}
          options={BUDGET_OPTIONS}
          onChange={(budget_inr) => onChange({ budget_inr })}
        />
      </Field>
    </div>
  );
}
