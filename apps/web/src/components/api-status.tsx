import { fetchDataStatus, fetchHealth } from "@/lib/api";

export async function ApiStatus() {
  try {
    const [health, data] = await Promise.all([
      fetchHealth(),
      fetchDataStatus(),
    ]);

    return (
      <section className="space-y-3">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 dark:border-emerald-900 dark:bg-emerald-950/30">
          <p className="text-sm font-medium text-emerald-800 dark:text-emerald-300">
            API connected
          </p>
          <p className="mt-1 text-sm text-emerald-700/80 dark:text-emerald-400/80">
            {health.app} · Supabase{" "}
            {health.supabase_configured ? "configured" : "not configured"}
          </p>
        </div>
        <div className="rounded-xl border border-violet-200 bg-violet-50/50 p-4 dark:border-violet-900 dark:bg-violet-950/30">
          <p className="text-sm font-medium text-violet-800 dark:text-violet-300">
            Seed data loaded
          </p>
          <p className="mt-1 text-sm text-violet-700/80 dark:text-violet-400/80">
            {data.careers_count} careers · {data.resources_count} resources ·{" "}
            {data.jd_total_count} JDs across {data.jd_roles_count} roles
            {data.data_valid ? "" : " · validation issues"}
          </p>
        </div>
      </section>
    );
  } catch {
    return (
      <section className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 dark:border-amber-900 dark:bg-amber-950/30">
        <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
          API offline
        </p>
        <p className="mt-1 text-sm text-amber-700/80 dark:text-amber-400/80">
          Start FastAPI on port 8000, then refresh.
        </p>
      </section>
    );
  }
}
