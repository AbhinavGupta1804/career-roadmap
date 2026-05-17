"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AgentReel } from "@/components/plan/agent-reel";
import { MissionLaunch } from "@/components/plan/mission-launch";
import { MissionPlanDashboard } from "@/components/plan/mission-plan-dashboard";
import { TrackSelection } from "@/components/plan/track-selection";
import {
  fetchPlan,
  fetchPlanByIntake,
  selectPlanTrack,
  startPlan,
  type PlanResponse,
} from "@/lib/api";
import type { TrackType } from "@/lib/schemas/agents";

type PlanFlowProps = {
  /** Plan UUID or intake submission UUID (legacy URLs). */
  routeId: string;
};

type Phase =
  | "loading"
  | "starting"
  | "track_pick"
  | "generating"
  | "completed"
  | "error";

export function PlanFlow({ routeId }: PlanFlowProps) {
  const router = useRouter();
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [pipelineDone, setPipelineDone] = useState(false);
  /** True while we await PATCH /track (response already has final plan). */
  const [awaitingTrackPatch, setAwaitingTrackPatch] = useState(false);

  const resolvePlan = useCallback(async (): Promise<PlanResponse> => {
    try {
      return await fetchPlan(routeId);
    } catch {
      return fetchPlanByIntake(routeId);
    }
  }, [routeId]);

  const applyPlan = useCallback((p: PlanResponse) => {
    setPlan(p);
    if (
      p.status === "awaiting_track_choice" &&
      p.agent_outputs.ai_reality_check
    ) {
      setPhase("track_pick");
    } else if (p.status === "generating") {
      setPhase("generating");
      setPipelineDone(false);
    } else if (p.status === "completed") {
      setPhase("completed");
      setPipelineDone(true);
    } else if (
      p.status === "pending" ||
      p.status === "failed" ||
      p.status === "picking_tracks"
    ) {
      setPhase("starting");
    } else {
      setPhase("track_pick");
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setPhase("loading");
      setError(null);
      try {
        const p = await resolvePlan();
        if (!cancelled) {
          if (p.plan_id !== routeId) {
            router.replace(`/plan/${p.plan_id}`);
          }
          applyPlan(p);
        }
      } catch {
        try {
          const started = await startPlan(routeId);
          if (!cancelled) {
            router.replace(`/plan/${started.plan_id}`);
            applyPlan(started);
          }
        } catch (e) {
          if (!cancelled) {
            setError(
              e instanceof Error ? e.message : "Could not load mission plan",
            );
            setPhase("error");
          }
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [routeId, resolvePlan, applyPlan, router]);

  useEffect(() => {
    // Only poll after a page reload mid-generation — not during our own PATCH call.
    if (
      phase !== "generating" ||
      !plan ||
      pipelineDone ||
      awaitingTrackPatch
    ) {
      return;
    }

    let cancelled = false;
    const poll = window.setInterval(async () => {
      try {
        const fresh = await fetchPlan(plan.plan_id);
        if (cancelled) return;
        if (fresh.status === "completed") {
          setPlan(fresh);
          setPipelineDone(true);
          setPhase("completed");
        } else if (fresh.status === "failed") {
          setError("Plan generation failed. Try again.");
          setPhase("error");
        }
      } catch {
        /* keep polling */
      }
    }, 1500);

    return () => {
      cancelled = true;
      window.clearInterval(poll);
    };
  }, [phase, plan, pipelineDone, awaitingTrackPatch]);

  async function handleConfirmTrack(trackType: TrackType) {
    if (!plan) return;
    setSubmitting(true);
    setAwaitingTrackPatch(true);
    setError(null);
    setPhase("generating");
    setPipelineDone(false);

    try {
      const updated = await selectPlanTrack(plan.plan_id, trackType);
      setPlan(updated);
      setPipelineDone(true);
      setPhase("completed");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to build mission plan");
      setPhase("track_pick");
    } finally {
      setSubmitting(false);
      setAwaitingTrackPatch(false);
    }
  }

  if (phase === "starting") {
    return <MissionLaunch intakeId={plan?.intake_id ?? routeId} />;
  }

  if (phase === "loading") {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-violet-600 border-t-transparent" />
        <p className="mt-4 text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Loading your mission plan…
        </p>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">
        <p className="font-medium">Something went wrong</p>
        <p className="mt-2">{error ?? "Unknown error"}</p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-4 rounded-full bg-red-700 px-4 py-2 text-xs font-medium text-white"
        >
          Retry
        </button>
      </div>
    );
  }

  if (phase === "track_pick" && plan?.agent_outputs.ai_reality_check) {
    return (
      <TrackSelection
        reality={plan.agent_outputs.ai_reality_check}
        defaultTrack="Realistic"
        submitting={submitting}
        onConfirm={handleConfirmTrack}
      />
    );
  }

  if (phase === "generating") {
    const label = plan?.chosen_track_type
      ? `${plan.chosen_track_type} track`
      : undefined;
    return (
      <div className="space-y-12 py-6">
        <AgentReel pipelineDone={pipelineDone} chosenTrackLabel={label} />
        {error ? (
          <p className="text-center text-sm text-red-600">{error}</p>
        ) : null}
      </div>
    );
  }

  if (phase === "completed" && plan) {
    return <MissionPlanDashboard plan={plan} />;
  }

  return (
    <p className="text-sm text-zinc-500">
      No track data yet.{" "}
      <button
        type="button"
        className="text-violet-600 underline"
        onClick={() =>
          void startPlan(plan?.intake_id ?? routeId).then(applyPlan)
        }
      >
        Run career analysis
      </button>
    </p>
  );
}
