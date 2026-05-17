import { fetchDataStatus, fetchHealth } from "@/lib/api";

export async function LandingApiStatus() {
  try {
    const [health, data] = await Promise.all([
      fetchHealth(),
      fetchDataStatus(),
    ]);

    return (
      <div className="flex flex-wrap gap-3">
        <StatusPill ok label="API online" detail={health.app} />
        <StatusPill
          ok={data.data_valid}
          label="Seed data"
          detail={`${data.careers_count} careers · ${data.jd_total_count} JDs`}
        />
        <StatusPill
          ok={health.supabase_configured}
          label="Supabase"
          detail={health.supabase_configured ? "Connected" : "Optional"}
        />
      </div>
    );
  } catch {
    return (
      <StatusPill
        ok={false}
        label="API offline"
        detail="Start FastAPI on port 8000, then refresh"
      />
    );
  }
}

function StatusPill({
  ok,
  label,
  detail,
}: {
  ok: boolean;
  label: string;
  detail: string;
}) {
  return (
    <div
      className={`rounded-xl border px-3 py-2 ${
        ok
          ? "border-emerald-200 bg-emerald-50/50 dark:border-emerald-900 dark:bg-emerald-950/30"
          : "border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/30"
      }`}
    >
      <p
        className={`text-xs font-semibold ${
          ok
            ? "text-emerald-800 dark:text-emerald-300"
            : "text-amber-800 dark:text-amber-300"
        }`}
      >
        {label}
      </p>
      <p className="text-xs text-zinc-600 dark:text-zinc-400">{detail}</p>
    </div>
  );
}
