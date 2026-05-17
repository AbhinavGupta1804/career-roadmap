"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { startPlan } from "@/lib/api";

const LAUNCH_AGENTS = [
  {
    id: "submit",
    title: "Profile saved",
    subtitle: "Your intake is in the system",
  },
  {
    id: "career_path_picker",
    title: "Career Path Picker",
    subtitle: "Scoring 68+ roles against your skills and interests",
  },
  {
    id: "ai_reality_check",
    title: "AI Reality Check",
    subtitle: "Building Stretch, Realistic and Safe tracks",
  },
] as const;

const STEP_MS = 900;

type MissionLaunchProps = {
  intakeId: string;
};

export function MissionLaunch({ intakeId }: MissionLaunchProps) {
  const router = useRouter();
  const [activeIndex, setActiveIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [apiDone, setApiDone] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const stepTimer = setInterval(() => {
      setActiveIndex((i) => Math.min(i + 1, LAUNCH_AGENTS.length - 2));
    }, STEP_MS);

    async function run() {
      try {
        const plan = await startPlan(intakeId);
        if (cancelled) return;
        setApiDone(true);
        setActiveIndex(LAUNCH_AGENTS.length - 1);
        await new Promise((r) => setTimeout(r, 700));
        router.replace(`/plan/${plan.plan_id}`);
      } catch (e) {
        if (!cancelled) {
          setError(
            e instanceof Error
              ? e.message
              : "Could not start your mission plan",
          );
        }
      }
    }

    void run();

    return () => {
      cancelled = true;
      clearInterval(stepTimer);
    };
  }, [intakeId, router]);

  const progressPct = Math.round(
    ((activeIndex + (apiDone ? 1 : 0.35)) / LAUNCH_AGENTS.length) * 100,
  );

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-lg flex-col justify-center py-12">
      <div className="text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-violet-600 dark:text-violet-400">
          Mission control
        </p>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-3xl">
          {error ? "Launch paused" : "Building your roadmap"}
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          {error
            ? "We could not finish the first agent pass."
            : "Your AI squad is analyzing careers and drafting three tracks."}
        </p>
      </div>

      <div className="mt-8">
        <div className="mb-2 flex justify-between text-xs font-medium text-zinc-500">
          <span>Progress</span>
          <span>{Math.min(progressPct, 100)}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-violet-600 to-emerald-500 transition-all duration-500 ease-out"
            style={{ width: `${Math.min(progressPct, 100)}%` }}
          />
        </div>
      </div>

      <ul className="mt-8 space-y-3">
        {LAUNCH_AGENTS.map((agent, index) => {
          const isDone = apiDone ? index <= activeIndex : index < activeIndex;
          const isActive = !apiDone && !error && index === activeIndex;

          return (
            <li
              key={agent.id}
              className={`flex items-center gap-4 rounded-2xl border px-4 py-3.5 transition-all duration-300 ${
                isActive
                  ? "agent-reel-active border-violet-400 bg-violet-50/90 dark:border-violet-600 dark:bg-violet-950/50"
                  : isDone
                    ? "border-emerald-300/80 bg-emerald-50/40 dark:border-emerald-800 dark:bg-emerald-950/30"
                    : "border-zinc-200 opacity-45 dark:border-zinc-800"
              }`}
            >
              <span
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${
                  isActive
                    ? "bg-violet-200 text-violet-800 dark:bg-violet-900 dark:text-violet-200"
                    : isDone
                      ? "bg-emerald-200 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200"
                      : "bg-zinc-100 text-zinc-400 dark:bg-zinc-800"
                }`}
              >
                {isDone ? "\u2713" : index + 1}
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-medium text-zinc-900 dark:text-zinc-50">
                  {agent.title}
                </p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  {agent.subtitle}
                </p>
              </div>
              {isActive ? (
                <span className="agent-reel-pulse h-2.5 w-2.5 shrink-0 rounded-full bg-violet-500" />
              ) : null}
            </li>
          );
        })}
      </ul>

      {!error ? (
        <p className="mt-8 text-center text-xs text-zinc-500">
          Usually 10-30 seconds. Do not close this tab.
        </p>
      ) : (
        <div className="mt-8 space-y-3 text-center">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-full bg-violet-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-violet-500"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  );
}
