import { SiteHeader } from "@/components/site-header";
import { PlanFlow } from "@/components/plan/plan-flow";

type PlanPageProps = {
  params: Promise<{ id: string }>;
};

export default async function PlanPage({ params }: PlanPageProps) {
  const { id } = await params;

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-5xl flex-1 px-4 py-10 sm:px-6 sm:py-12">
        <PlanFlow routeId={id} />
      </main>
    </>
  );
}
