"use client";

import { useCallback, useEffect, useState } from "react";
import type { PlanResponse } from "@/lib/api";
import { API_BASE } from "@/lib/api";

type WeekProgress = {
  completed_weeks: number[];
  current_streak: number;
  longest_streak: number;
  last_check_in: string | null;
};

type WeeklyCheckInProps = {
  plan: PlanResponse;
  onProgressChange?: (progress: WeekProgress) => void;
};

const DEMO_STORAGE_KEY = "demo-week-progress";

function loadDemoProgress(): WeekProgress {
  if (typeof window === "undefined") {
    return { completed_weeks: [], current_streak: 0, longest_streak: 0, last_check_in: null };
  }
  try {
    const raw = localStorage.getItem(DEMO_STORAGE_KEY);
    if (raw) return JSON.parse(raw) as WeekProgress;
  } catch {
    /* ignore */
  }
  return { completed_weeks: [], current_streak: 0, longest_streak: 0, last_check_in: null };
}

function saveDemoProgress(progress: WeekProgress) {
  localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(progress));
}

export function WeeklyCheckIn({ plan, onProgressChange }: WeeklyCheckInProps) {
  const weeks = plan.agent_outputs.learning_path?.weeks ?? [];
  const totalWeeks = plan.agent_outputs.learning_path?.total_weeks ?? weeks.length;
  const isDemo = plan.plan_id === "demo";

  const [progress, setProgress] = useState<WeekProgress>(
    plan.week_progress ?? {
      completed_weeks: [],
      current_streak: 0,
      longest_streak: 0,
      last_check_in: null,
    },
  );
  const [pendingWeek, setPendingWeek] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isDemo) {
      const demo = loadDemoProgress();
      setProgress(demo);
      onProgressChange?.(demo);
    } else if (plan.week_progress) {
      setProgress(plan.week_progress as WeekProgress);
    }
  }, [isDemo, plan.week_progress, onProgressChange]);

  const toggleWeek = useCallback(
    async (weekNum: number, currentlyDone: boolean) => {
      setError(null);
      setPendingWeek(weekNum);

      try {
        if (isDemo) {
          const completed = new Set(progress.completed_weeks);
          if (currentlyDone) completed.delete(weekNum);
          else completed.add(weekNum);
          const ordered = [...completed].sort((a, b) => a - b);
          let current = 0;
          let expect = ordered.at(-1) ?? 0;
          for (const w of [...ordered].reverse()) {
            if (w === expect) {
              current += 1;
              expect -= 1;
            } else break;
          }
          let longest = progress.longest_streak;
          let run = 1;
          for (let i = 1; i < ordered.length; i++) {
            if (ordered[i] === ordered[i - 1] + 1) {
              run += 1;
              longest = Math.max(longest, run);
            } else run = 1;
          }
          longest = Math.max(longest, current, run);
          const next: WeekProgress = {
            completed_weeks: ordered,
            current_streak: current,
            longest_streak: longest,
            last_check_in: new Date().toISOString().slice(0, 10),
          };
          saveDemoProgress(next);
          setProgress(next);
          onProgressChange?.(next);
        } else {
          const res = await fetch(`${API_BASE}/api/plans/${plan.plan_id}/progress`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ week: weekNum, done: !currentlyDone }),
          });
          if (!res.ok) {
            const body = (await res.json()) as { detail?: string };
            throw new Error(body.detail ?? `Failed (${res.status})`);
          }
          const next = (await res.json()) as WeekProgress;
          setProgress(next);
          onProgressChange?.(next);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not save progress");
      } finally {
        setPendingWeek(null);
      }
    },
    [isDemo, plan.plan_id, progress.completed_weeks, progress.longest_streak, onProgressChange],
  );

  if (totalWeeks < 1) {
    return null;
  }

  const doneCount = progress.completed_weeks.length;
  const pct = Math.round((doneCount / totalWeeks) * 100);

  return (
    <div className="rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50/40 p-5 dark:border-amber-900 dark:from-amber-950/40 dark:to-orange-950/20">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-amber-700 dark:text-amber-400">
            Weekly check-in
          </p>
          <h2 className="mt-1 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            {doneCount} of {totalWeeks} weeks complete
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Mark each week done when you finish the focus skill and mini-task.
          </p>
        </div>
        <div className="flex gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
              {progress.current_streak}
            </p>
            <p className="text-xs text-zinc-500">Current streak</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-zinc-700 dark:text-zinc-300">
              {progress.longest_streak}
            </p>
            <p className="text-xs text-zinc-500">Best streak</p>
          </div>
        </div>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-amber-100 dark:bg-amber-950">
        <div
          className="h-full rounded-full bg-amber-500 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>

      <ul className="mt-4 grid gap-2 sm:grid-cols-2">
        {weeks.map((w) => {
          const done = progress.completed_weeks.includes(w.week);
          const loading = pendingWeek === w.week;
          return (
            <li
              key={w.week}
              className={`flex items-start gap-3 rounded-xl border p-3 text-sm transition ${
                done
                  ? "border-emerald-300 bg-emerald-50/80 dark:border-emerald-800 dark:bg-emerald-950/30"
                  : "border-zinc-200 bg-white/80 dark:border-zinc-700 dark:bg-zinc-900/50"
              }`}
            >
              <button
                type="button"
                disabled={loading}
                onClick={() => void toggleWeek(w.week, done)}
                className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border text-xs font-bold ${
                  done
                    ? "border-emerald-600 bg-emerald-600 text-white"
                    : "border-zinc-300 bg-white text-transparent hover:border-amber-500 dark:border-zinc-600 dark:bg-zinc-800"
                }`}
                aria-label={done ? `Mark week ${w.week} incomplete` : `Mark week ${w.week} done`}
              >
                {loading ? "…" : "✓"}
              </button>
              <div className="min-w-0">
                <p className="font-medium text-zinc-900 dark:text-zinc-50">
                  Week {w.week}: {w.focus_skill}
                  {w.checkpoint ? (
                    <span className="ml-1 rounded bg-violet-100 px-1.5 py-0.5 text-xs text-violet-700 dark:bg-violet-950 dark:text-violet-300">
                      checkpoint
                    </span>
                  ) : null}
                </p>
                <p className="mt-0.5 line-clamp-2 text-xs text-zinc-500">{w.mini_task}</p>
              </div>
            </li>
          );
        })}
      </ul>

      {progress.last_check_in ? (
        <p className="mt-3 text-xs text-zinc-500">Last check-in: {progress.last_check_in}</p>
      ) : null}
      {error ? <p className="mt-2 text-xs text-red-600 dark:text-red-400">{error}</p> : null}
    </div>
  );
}
