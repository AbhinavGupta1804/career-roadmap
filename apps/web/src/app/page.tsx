import Link from "next/link";

import { SiteHeader } from "@/components/site-header";
import { ApiStatus } from "@/components/api-status";

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto flex max-w-5xl flex-1 flex-col gap-10 px-4 py-16 sm:px-6">
        <section className="max-w-2xl space-y-4">
          <p className="text-sm font-medium uppercase tracking-wider text-violet-600">
            Skill-to-Job Roadmap
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-5xl">
            Your 12-month career plan, built by an AI team
          </h1>
          <p className="text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            For Indian students and freshers in tech streams. Tell us your
            profile and interests — get three realistic paths, an AI reality
            check, and a week-by-week mission plan.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/intake"
              className="inline-flex h-11 items-center justify-center rounded-full bg-violet-600 px-6 text-sm font-medium text-white transition hover:bg-violet-500"
            >
              Build my roadmap
            </Link>
            <Link
              href="/plan/demo"
              className="inline-flex h-11 items-center justify-center rounded-full border border-zinc-300 px-6 text-sm font-medium text-zinc-700 transition hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
            >
              Preview plan layout
            </Link>
          </div>
        </section>
        <ApiStatus />
      </main>
    </>
  );
}
