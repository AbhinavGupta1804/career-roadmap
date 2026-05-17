import { SiteHeader } from "@/components/site-header";
import { MissionLaunch } from "@/components/plan/mission-launch";

type LaunchPageProps = {
  params: Promise<{ submissionId: string }>;
};

export default async function IntakeLaunchPage({ params }: LaunchPageProps) {
  const { submissionId } = await params;

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-2xl flex-1 px-4 py-8 sm:px-6">
        <MissionLaunch intakeId={submissionId} />
      </main>
    </>
  );
}
