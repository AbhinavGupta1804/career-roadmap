"use client";

import {
  COMMON_SKILLS,
  GOAL_OPTIONS,
  SALARY_OPTIONS,
  SKILL_RATING_OPTIONS,
  TIMELINE_OPTIONS,
} from "@/lib/intake-constants";
import type { SkillsAndGoals, StudentSkill } from "@/lib/schemas/intake";
import {
  Field,
  RadioGroup,
  SelectInput,
  TextArea,
  TextInput,
} from "@/components/intake/form-primitives";

type Props = {
  value: Partial<SkillsAndGoals> & { dream_companies?: string[] };
  errors: Record<string, string>;
  onChange: (
    patch: Partial<SkillsAndGoals> & { dream_companies?: string[] },
  ) => void;
};

export function StepSkills({ value, errors, onChange }: Props) {
  const skills = value.skills ?? [];
  const companies = value.dream_companies ?? ["", "", ""];

  function skillRating(name: string): StudentSkill["rating"] | undefined {
    return skills.find((s) => s.name === name)?.rating;
  }

  function setSkillRating(name: string, rating: StudentSkill["rating"]) {
    const rest = skills.filter((s) => s.name !== name);
    onChange({ skills: [...rest, { name, rating }] });
  }

  function clearSkill(name: string) {
    onChange({ skills: skills.filter((s) => s.name !== name) });
  }

  return (
    <div className="space-y-5">
      <Field
        label="Tools & languages you've touched"
        hint="Select a rating for each skill you know."
      >
        <div className="space-y-3">
          {COMMON_SKILLS.map((name) => {
            const rating = skillRating(name);
            return (
              <div
                key={name}
                className="flex flex-col gap-2 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between"
              >
                <span className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  {name}
                </span>
                <SelectInput
                  className="sm:max-w-[220px]"
                  value={rating ?? ""}
                  onChange={(e) => {
                    const v = e.target.value as StudentSkill["rating"] | "";
                    if (!v) clearSkill(name);
                    else setSkillRating(name, v);
                  }}
                >
                  <option value="">Not selected</option>
                  {SKILL_RATING_OPTIONS.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </SelectInput>
              </div>
            );
          })}
        </div>
      </Field>

      <Field label="Projects (optional)" error={errors.projects_text}>
        <TextArea
          placeholder="Briefly describe any college/personal projects..."
          value={value.projects_text ?? ""}
          onChange={(e) => onChange({ projects_text: e.target.value })}
        />
      </Field>

      <Field label="GitHub profile (optional)" error={errors.github_url}>
        <TextInput
          type="url"
          placeholder="https://github.com/username"
          value={value.github_url ?? ""}
          onChange={(e) => onChange({ github_url: e.target.value })}
        />
      </Field>

      <Field label="Any internship or freelance experience?">
        <RadioGroup
          name="has_internship"
          value={value.has_internship === true ? "Yes" : value.has_internship === false ? "No" : undefined}
          options={["Yes", "No"] as const}
          onChange={(v) =>
            onChange({
              has_internship: v === "Yes",
              internship_brief: v === "Yes" ? value.internship_brief : "",
            })
          }
        />
      </Field>

      {value.has_internship ? (
        <Field label="Internship / freelance details">
          <TextArea
            placeholder="Role, company, what you did..."
            value={value.internship_brief ?? ""}
            onChange={(e) => onChange({ internship_brief: e.target.value })}
          />
        </Field>
      ) : null}

      <Field label="Primary goal" error={errors.primary_goal}>
        <RadioGroup
          name="primary_goal"
          value={value.primary_goal}
          options={GOAL_OPTIONS}
          onChange={(primary_goal) => onChange({ primary_goal })}
        />
      </Field>

      <Field label="Target salary band" error={errors.target_salary_band}>
        <RadioGroup
          name="target_salary_band"
          value={value.target_salary_band}
          options={SALARY_OPTIONS}
          onChange={(target_salary_band) => onChange({ target_salary_band })}
        />
      </Field>

      <Field label="Timeline to job" error={errors.timeline_to_job}>
        <RadioGroup
          name="timeline_to_job"
          value={value.timeline_to_job}
          options={TIMELINE_OPTIONS}
          onChange={(timeline_to_job) => onChange({ timeline_to_job })}
        />
      </Field>

      <Field
        label="Dream companies (up to 3)"
        hint="Optional — helps tailor your plan."
      >
        <div className="space-y-2">
          {[0, 1, 2].map((i) => (
            <TextInput
              key={i}
              placeholder={`Company ${i + 1}`}
              value={companies[i] ?? ""}
              onChange={(e) => {
                const next = [...companies];
                next[i] = e.target.value;
                onChange({ dream_companies: next });
              }}
            />
          ))}
        </div>
      </Field>
    </div>
  );
}
