"use client";

import type { CareerTrack, TrackType } from "@/lib/schemas/agents";
import { RISK_TIER_STYLES } from "@/lib/agent-meta";

const TYPE_ACCENTS: Record<
  TrackType,
  { label: string; border: string; selected: string }
> = {
  Stretch: {
    label: "Ambitious",
    border: "border-violet-300 dark:border-violet-800",
    selected: "ring-violet-500 bg-violet-50/50 dark:bg-violet-950/30",
  },
  Realistic: {
    label: "Recommended",
    border: "border-emerald-300 dark:border-emerald-800",
    selected: "ring-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/30",
  },
  Safe: {
    label: "Lower risk",
    border: "border-zinc-300 dark:border-zinc-700",
    selected: "ring-zinc-500 bg-zinc-50/50 dark:bg-zinc-900/50",
  },
};

type TrackCardProps = {
  track: CareerTrack;
  selected: boolean;
  onSelect: () => void;
};

export function TrackCard({ track, selected, onSelect }: TrackCardProps) {
  const accent = TYPE_ACCENTS[track.type];
  const tier = track.ai_risk_tier ?? 3;
  const risk = RISK_TIER_STYLES[tier] ?? RISK_TIER_STYLES[3];

  return (
    <button
      type="button"
      onClick={onSelect}
      className={`group w-full rounded-2xl border p-5 text-left transition-all duration-200 ${
        accent.border
      } ${
        selected
          ? `ring-2 ${accent.selected} ${risk.ring}`
          : "border-zinc-200 hover:border-violet-300 dark:border-zinc-800 dark:hover:border-violet-700"
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide text-violet-600 dark:text-violet-400">
            {track.type}
          </span>
          <span className="ml-2 text-xs text-zinc-500">· {accent.label}</span>
          <h3 className="mt-1 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            {track.name}
          </h3>
        </div>
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${risk.badge}`}
        >
          Tier {tier} · {track.ai_risk_label ?? risk.label}
        </span>
      </div>

      <p className="mt-3 text-sm font-medium text-zinc-800 dark:text-zinc-200">
        {track.avg_starting_salary_band}
        <span className="font-normal text-zinc-500">
          {" "}
          · ~{track.time_to_job_estimate_months} mo to first offer
        </span>
      </p>

      <p className="mt-3 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
        {track.why_recommended}
      </p>

      {track.honest_warning ? (
        <p className="mt-3 rounded-lg border border-amber-200/80 bg-amber-50/80 px-3 py-2 text-xs leading-relaxed text-amber-900 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-200">
          ⚠ {track.honest_warning}
        </p>
      ) : null}

      {track.top_hiring_companies.length > 0 ? (
        <p className="mt-3 text-xs text-zinc-500">
          Hiring: {track.top_hiring_companies.slice(0, 4).join(" · ")}
        </p>
      ) : null}

      <div
        className={`mt-4 flex h-5 w-5 items-center justify-center rounded-full border-2 ${
          selected
            ? "border-violet-600 bg-violet-600"
            : "border-zinc-300 dark:border-zinc-600"
        }`}
      >
        {selected ? (
          <span className="h-2 w-2 rounded-full bg-white" />
        ) : null}
      </div>
    </button>
  );
}
