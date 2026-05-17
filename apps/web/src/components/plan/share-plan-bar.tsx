"use client";

import { useCallback, useState } from "react";
import type { PlanResponse } from "@/lib/api";
import { downloadPlanPdf } from "@/lib/api";

type SharePlanBarProps = {
  plan: PlanResponse;
};

export function SharePlanBar({ plan }: SharePlanBarProps) {
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const isDemo = plan.plan_id === "demo";

  const shareUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}/plan/${plan.plan_id}`
      : `/plan/${plan.plan_id}`;

  const copyLink = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* user can copy from address bar */
    }
  }, [shareUrl]);

  const exportPdf = useCallback(async () => {
    setExportError(null);
    setExporting(true);
    try {
      await downloadPlanPdf(plan);
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  }, [plan]);

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-zinc-50/80 px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900/50">
      {!isDemo ? (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
              Shareable link
            </p>
            <p className="truncate font-mono text-sm text-zinc-700 dark:text-zinc-300">
              {shareUrl}
            </p>
          </div>
          <button
            type="button"
            onClick={() => void copyLink()}
            className="shrink-0 rounded-full border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
          >
            {copied ? "Copied!" : "Copy link"}
          </button>
        </div>
      ) : (
        <p className="text-xs text-zinc-500">
          Demo preview — export a sample PDF or{" "}
          <a href="/intake" className="font-medium text-violet-600 underline">
            start intake
          </a>{" "}
          for your full plan.
        </p>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => void exportPdf()}
          disabled={exporting || plan.status !== "completed"}
          className="rounded-full bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {exporting ? "Generating PDF…" : "Download PDF"}
        </button>
        {plan.status !== "completed" ? (
          <span className="text-xs text-zinc-500">Available when your plan is complete</span>
        ) : null}
      </div>
      {exportError ? (
        <p className="text-xs text-red-600 dark:text-red-400">{exportError}</p>
      ) : null}
    </div>
  );
}
