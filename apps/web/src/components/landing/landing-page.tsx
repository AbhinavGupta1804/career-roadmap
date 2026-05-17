import Link from "next/link";

import { LandingApiStatus } from "@/components/landing/landing-api-status";
import { ArrowRightIcon } from "@/components/landing/icons";
import { SiteHeader } from "@/components/site-header";
import { AGENT_REEL } from "@/lib/agent-meta";
import { BRANCH_OPTIONS } from "@/lib/intake-constants";

const STATS = [
  { value: "7", label: "AI specialists", detail: "on your career squad" },
  { value: "68+", label: "Career paths", detail: "tech & commerce" },
  { value: "1.3k", label: "Real JDs", detail: "Indian fresher roles" },
  { value: "12", label: "Week plan", detail: "skills + projects" },
] as const;

const STEPS = [
  {
    step: "01",
    title: "Share your profile",
    body: "Branch, city, skills, interests, and goals — CS, Commerce, BBA, and more.",
  },
  {
    step: "02",
    title: "Pick your track",
    body: "Stretch, Realistic, and Safe paths with salary bands and honest AI-risk warnings.",
  },
  {
    step: "03",
    title: "Run the mission",
    body: "Weekly learning, portfolio projects, certs to skip, and LinkedIn momentum.",
  },
] as const;

const AGENT_ICONS: Record<string, string> = {
  career_path_picker: "M12 2 4 7v10l8 5 8-5V7l-8-5z",
  ai_reality_check: "M13 2 3 14h7l-1 8 10-12h-7l1-8z",
  skill_gap_analyzer: "M4 19V5M12 19V9M20 19v-6",
  learning_path_generator: "M7 3v4M17 3v4M4 9h16M6 13h4M14 13h4M6 17h4M14 17h4",
  project_ideator: "M14 10l-2 2-4-4M8 21h8a2 2 0 002-2V7l-5-5H8a2 2 0 00-2 2v15a2 2 0 002 2z",
  certification_advisor: "M12 14l9-5-9-5-9 5 9 5zm0 0v7",
  portfolio_builder: "M4 16l4-4 4 4 8-10",
};

export function LandingPage() {
  return (
    <div className="landing-page relative min-h-screen overflow-hidden bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <div className="landing-glow landing-glow-a pointer-events-none" aria-hidden />
      <div className="landing-glow landing-glow-b pointer-events-none" aria-hidden />
      <div className="landing-grid pointer-events-none absolute inset-0" aria-hidden />

      <SiteHeader />

      <main className="relative">
        <section className="mx-auto max-w-5xl px-4 pb-20 pt-12 sm:px-6 sm:pt-16 lg:pb-24">
          <div className="mx-auto max-w-3xl text-center">
            <p className="landing-fade-in mb-6 inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-4 py-1.5 text-xs font-medium uppercase tracking-wider text-violet-700 dark:border-violet-800 dark:bg-violet-950/50 dark:text-violet-300">
              <span className="h-1.5 w-1.5 rounded-full bg-violet-600 dark:bg-violet-400" />
              Skill-to-job · India 2026
            </p>
            <h1 className="landing-fade-in landing-fade-in-delay-1 text-4xl font-semibold leading-[1.1] tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-5xl">
              Your personal{" "}
              <span className="text-violet-600 dark:text-violet-400">
                AI career squad
              </span>
            </h1>
            <p className="landing-fade-in landing-fade-in-delay-2 mx-auto mt-6 max-w-2xl text-base leading-relaxed text-zinc-600 dark:text-zinc-400 sm:text-lg">
              For Indian students and freshers — engineering, commerce, and
              business streams. One intake builds three realistic tracks, a
              week-by-week roadmap, portfolio projects, and an honest AI reality
              check.
            </p>
          </div>

          <div className="landing-fade-in landing-fade-in-delay-3 mt-12 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {STATS.map((stat) => (
              <div
                key={stat.label}
                className="landing-stat-card rounded-2xl border border-zinc-200 bg-white p-4 text-center shadow-sm transition hover:border-violet-200 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900/50 sm:p-5"
              >
                <p className="text-2xl font-bold text-violet-600 dark:text-violet-400 sm:text-3xl">
                  {stat.value}
                </p>
                <p className="mt-1 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                  {stat.label}
                </p>
                <p className="mt-0.5 text-xs text-zinc-500">{stat.detail}</p>
              </div>
            ))}
          </div>

          <div className="landing-fade-in landing-fade-in-delay-4 mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/intake"
              className="group inline-flex h-11 min-w-[220px] items-center justify-center gap-2 rounded-full bg-violet-600 px-8 text-sm font-medium text-white transition hover:bg-violet-500"
            >
              Build my roadmap
              <ArrowRightIcon className="transition group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/plan/demo"
              className="inline-flex h-11 min-w-[200px] items-center justify-center rounded-full border border-zinc-300 bg-white px-8 text-sm font-medium text-zinc-700 transition hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              Preview sample plan
            </Link>
          </div>
          <p className="mt-4 text-center text-xs text-zinc-500">
            ~5 min intake · No payment · Export PDF when your plan is ready
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-2">
            {BRANCH_OPTIONS.map((branch) => (
              <span
                key={branch}
                className="rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400"
              >
                {branch}
              </span>
            ))}
          </div>
        </section>

        <section className="border-y border-zinc-200 bg-zinc-50/80 py-16 dark:border-zinc-800 dark:bg-zinc-900/40 sm:py-20">
          <div className="mx-auto max-w-5xl px-4 sm:px-6">
            <p className="text-center text-xs font-semibold uppercase tracking-widest text-violet-600 dark:text-violet-400">
              What runs for you
            </p>
            <h2 className="mt-3 text-center text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-3xl">
              Seven agents. One mission plan.
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-center text-sm text-zinc-600 dark:text-zinc-400">
              Orchestrated pipeline — from career fit to LinkedIn posts — tuned
              to Indian hiring data.
            </p>

            <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
              {AGENT_REEL.map((agent, i) => (
                <article
                  key={agent.id}
                  className="landing-agent-card group flex flex-col rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm transition hover:border-violet-300 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950 dark:hover:border-violet-700"
                  style={{ animationDelay: `${i * 60}ms` }}
                >
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl border border-violet-200 bg-violet-50 text-violet-600 transition group-hover:border-violet-300 dark:border-violet-800 dark:bg-violet-950/60 dark:text-violet-400">
                    <svg
                      viewBox="0 0 24 24"
                      className="h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden
                    >
                      <path d={AGENT_ICONS[agent.id] ?? "M12 6v12M6 12h12"} />
                    </svg>
                  </div>
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                    {agent.title}
                  </h3>
                  <p className="mt-1 flex-1 text-xs leading-relaxed text-zinc-500 dark:text-zinc-400">
                    {agent.subtitle}
                  </p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16 sm:py-20">
          <div className="mx-auto max-w-5xl px-4 sm:px-6">
            <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-violet-600 dark:text-violet-400">
                  How it works
                </p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
                  From confused fresher to{" "}
                  <span className="text-violet-600 dark:text-violet-400">
                    clear next steps
                  </span>
                </h2>
                <p className="mt-4 text-zinc-600 dark:text-zinc-400">
                  We score 68+ careers against your skills, interests, and
                  college tier — then generate a plan you can actually execute,
                  not generic advice.
                </p>
              </div>
              <ol className="space-y-4">
                {STEPS.map((item) => (
                  <li
                    key={item.step}
                    className="flex gap-4 rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900/50"
                  >
                    <span className="font-mono text-lg font-bold text-violet-600 dark:text-violet-400">
                      {item.step}
                    </span>
                    <div>
                      <h3 className="font-semibold text-zinc-900 dark:text-zinc-50">
                        {item.title}
                      </h3>
                      <p className="mt-1 text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
                        {item.body}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-5xl px-4 pb-8 sm:px-6">
          <div className="landing-cta relative overflow-hidden rounded-2xl border border-violet-200 bg-gradient-to-br from-violet-50 via-white to-zinc-50 px-6 py-12 text-center shadow-sm dark:border-violet-900 dark:from-violet-950/40 dark:via-zinc-950 dark:to-zinc-900 sm:px-12 sm:py-14">
            <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 sm:text-3xl">
              Ready to see your three tracks?
            </h2>
            <p className="mx-auto mt-3 max-w-lg text-sm text-zinc-600 dark:text-zinc-400 sm:text-base">
              Start with intake — pick Commerce, CS, BBA, or any supported
              branch. Your AI team handles the rest.
            </p>
            <Link
              href="/intake"
              className="mt-8 inline-flex h-11 items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 text-sm font-medium text-white transition hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
            >
              Start free intake
              <ArrowRightIcon />
            </Link>
          </div>
        </section>

        <section className="mx-auto max-w-5xl px-4 pb-16 sm:px-6">
          <div className="rounded-2xl border border-zinc-200 bg-zinc-50/50 p-4 dark:border-zinc-800 dark:bg-zinc-900/30">
            <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
              System status
            </p>
            <div className="mt-2">
              <LandingApiStatus />
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-zinc-200 py-8 dark:border-zinc-800">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 px-4 text-center text-xs text-zinc-500 sm:flex-row sm:px-6 sm:text-left">
          <p>
            © {new Date().getFullYear()} Career Roadmap · Built for Indian
            freshers
          </p>
          <div className="flex gap-4">
            <Link href="/plan/demo" className="hover:text-zinc-700 dark:hover:text-zinc-300">
              Demo plan
            </Link>
            <Link href="/intake" className="hover:text-zinc-700 dark:hover:text-zinc-300">
              Intake
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
