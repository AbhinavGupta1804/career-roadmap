"use client";

import { useEffect, useState } from "react";

import { AGENT_REEL } from "@/lib/agent-meta";

const STEP_MS = 520;

type AgentReelProps = {
  pipelineDone: boolean;
  chosenTrackLabel?: string;
};

export function AgentReel({ pipelineDone, chosenTrackLabel }: AgentReelProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    if (finished) return;

    if (pipelineDone && activeIndex >= AGENT_REEL.length - 1) {
      const t = window.setTimeout(() => setFinished(true), 400);
      return () => window.clearTimeout(t);
    }

    if (activeIndex >= AGENT_REEL.length - 1) return;

    const t = window.setTimeout(() => {
      setActiveIndex((i) => Math.min(i + 1, AGENT_REEL.length - 1));
    }, STEP_MS);

    return () => window.clearTimeout(t);
  }, [activeIndex, pipelineDone, finished]);

  useEffect(() => {
    if (!pipelineDone || finished) return;
    if (activeIndex < AGENT_REEL.length - 1) {
      const rush = window.setTimeout(() => {
        setActiveIndex(AGENT_REEL.length - 1);
      }, 280);
      return () => window.clearTimeout(rush);
    }
  }, [pipelineDone, finished, activeIndex]);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <p className="text-xs font-semibold uppercase tracking-widest text-violet-600 dark:text-violet-400">
          Mission plan in progress
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          {finished ? "Your plan is ready" : "7 agents at work"}
        </h2>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          {finished
            ? chosenTrackLabel
              ? `Locked on ${chosenTrackLabel} — scroll down for your roadmap.`
              : "All agents finished — scroll down for your roadmap."
            : "Watch each specialist run — this is your reel moment."}
        </p>
      </div>

      <ul className="mx-auto grid max-w-lg gap-3">
        {AGENT_REEL.map((agent, index) => {
          const state =
            index < activeIndex
              ? "done"
              : index === activeIndex && !finished
                ? "active"
                : index === activeIndex && finished
                  ? "done"
                  : "pending";

          return (
            <li
              key={agent.id}
              className={`agent-reel-card flex items-center gap-4 rounded-xl border px-4 py-3 transition-all duration-300 ${
                state === "active"
                  ? "agent-reel-active border-violet-400 bg-violet-50/90 dark:border-violet-600 dark:bg-violet-950/50"
                  : state === "done"
                    ? "border-emerald-300/80 bg-emerald-50/40 dark:border-emerald-800 dark:bg-emerald-950/30"
                    : "border-zinc-200 opacity-50 dark:border-zinc-800"
              }`}
            >
              <span
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-xl ${
                  state === "active"
                    ? "bg-violet-200 dark:bg-violet-900"
                    : state === "done"
                      ? "bg-emerald-200 dark:bg-emerald-900"
                      : "bg-zinc-100 dark:bg-zinc-800"
                }`}
              >
                {state === "done" ? "✓" : agent.emoji}
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-medium text-zinc-900 dark:text-zinc-50">
                  {agent.title}
                </p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  {agent.subtitle}
                </p>
              </div>
              {state === "active" && !finished ? (
                <span className="agent-reel-pulse h-2 w-2 shrink-0 rounded-full bg-violet-500" />
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
