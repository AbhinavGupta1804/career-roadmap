import { SiteHeader } from "@/components/site-header";
import { MissionPlanDashboard } from "@/components/plan/mission-plan-dashboard";
import { DEMO_PLAN } from "@/lib/demo-plan";

export default function DemoPlanPage() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-5xl flex-1 px-4 py-10 sm:px-6 sm:py-12">
        <PlanFlowBanner />
        <MissionPlanDashboard plan={DEMO_PLAN} />
      </main>
    </>
  );
}

function PlanFlowBanner() {
  return (
    <p className="mb-6 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2 text-sm text-violet-800 dark:border-violet-900 dark:bg-violet-950/40 dark:text-violet-200">
      Layout preview with sample data —{" "}
      <a href="/intake" className="font-medium underline">
        start intake
      </a>{" "}
      for your real plan.
    </p>
  );
}
