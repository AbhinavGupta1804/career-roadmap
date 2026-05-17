"use client";

import { useMemo, useState } from "react";

import { TrackCard } from "@/components/plan/track-card";
import type { AiRealityCheckOutput } from "@/lib/schemas/agents";
import type { TrackType } from "@/lib/schemas/agents";
import { TRACK_TYPE_ORDER } from "@/lib/agent-meta";

type TrackSelectionProps = {
  reality: AiRealityCheckOutput;
  defaultTrack?: TrackType;
  submitting: boolean;
  onConfirm: (trackType: TrackType) => void;
};

export function TrackSelection({
  reality,
  defaultTrack = "Realistic",
  submitting,
  onConfirm,
}: TrackSelectionProps) {
  const [selected, setSelected] = useState<TrackType>(defaultTrack);

  const orderedTracks = useMemo(() => {
    const byType = new Map(reality.tracks.map((t) => [t.type, t]));
    return TRACK_TYPE_ORDER.map((type) => byType.get(type)).filter(
      (t): t is NonNullable<typeof t> => Boolean(t),
    );
  }, [reality.tracks]);

  const briefing = reality.disruption_briefing;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Pick your path
        </h2>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Three AI-checked tracks — choose one before we build your skill gaps,
          weekly plan, and projects.{" "}
          <span className="font-medium text-emerald-700 dark:text-emerald-400">
            Realistic
          </span>{" "}
          is pre-selected for most profiles.
        </p>
      </div>

      {briefing.summary ? (
        <div className="rounded-xl border border-zinc-200 bg-zinc-50/80 p-4 text-sm dark:border-zinc-800 dark:bg-zinc-900/50">
          <p className="font-medium text-zinc-900 dark:text-zinc-100">
            AI disruption briefing
          </p>
          <p className="mt-2 leading-relaxed text-zinc-600 dark:text-zinc-400">
            {briefing.summary}
          </p>
          {briefing.do_not_pursue_callouts.length > 0 ? (
            <ul className="mt-3 space-y-1.5 text-xs text-amber-800 dark:text-amber-300">
              {briefing.do_not_pursue_callouts.map((line) => (
                <li key={line}>· {line}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-3">
        {orderedTracks.map((track) => (
          <TrackCard
            key={track.type}
            track={track}
            selected={selected === track.type}
            onSelect={() => setSelected(track.type)}
          />
        ))}
      </div>

      <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-zinc-500">
          This choice locks Agents 3–7 onto{" "}
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            {selected}
          </span>
          .
        </p>
        <button
          type="button"
          disabled={submitting}
          onClick={() => onConfirm(selected)}
          className="inline-flex h-12 items-center justify-center rounded-full bg-violet-600 px-8 text-sm font-semibold text-white transition hover:bg-violet-500 disabled:opacity-60"
        >
          {submitting
            ? "Building your mission plan…"
            : `Continue with ${selected} track`}
        </button>
      </div>
    </div>
  );
}
