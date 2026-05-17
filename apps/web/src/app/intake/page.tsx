import { SiteHeader } from "@/components/site-header";
import { IntakeWizard } from "@/components/intake/intake-wizard";

export default function IntakePage() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-2xl flex-1 px-4 py-8 pb-16 sm:px-6 sm:py-12">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-3xl">
            Build your roadmap
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
            ~5 minutes · Tech streams (CS, IT, ECE, EE) · We always produce a
            plan, including weaker profiles.
          </p>
        </div>
        <IntakeWizard />
      </main>
    </>
  );
}
