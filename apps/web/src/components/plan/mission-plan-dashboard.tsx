"use client";

import type { PlanResponse } from "@/lib/api";
import type { CareerTrack } from "@/lib/schemas/agents";
import { RISK_TIER_STYLES } from "@/lib/agent-meta";
import { PlanSection } from "@/components/plan/plan-section";
import { SharePlanBar } from "@/components/plan/share-plan-bar";
import { WeeklyCheckIn } from "@/components/plan/weekly-check-in";

const NAV = [
  { id: "track", label: "Your track" },
  { id: "disruption", label: "AI briefing" },
  { id: "gaps", label: "Skill gaps" },
  { id: "checkin", label: "Check-in" },
  { id: "weeks", label: "Weekly plan" },
  { id: "projects", label: "Projects" },
  { id: "certs", label: "Certifications" },
  { id: "phase2", label: "Outreach" },
] as const;

function findChosenTrack(plan: PlanResponse): CareerTrack | null {
  const type = plan.chosen_track_type;
  const tracks = plan.agent_outputs.ai_reality_check?.tracks;
  if (!type || !tracks) return null;
  return tracks.find((t) => t.type === type) ?? null;
}

const PRIORITY_STYLES = {
  must: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
  should: "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-300",
  nice: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
} as const;

type MissionPlanDashboardProps = {
  plan: PlanResponse;
};

export function MissionPlanDashboard({ plan }: MissionPlanDashboardProps) {
  const track = findChosenTrack(plan);
  const outputs = plan.agent_outputs;
  const briefing = outputs.ai_reality_check?.disruption_briefing;
  const gaps = outputs.skill_gap?.skills ?? [];
  const weeks = outputs.learning_path?.weeks ?? [];
  const projects = outputs.projects?.projects ?? [];
  const certs = outputs.certifications;
  const portfolio = outputs.portfolio;
  const isDemo = plan.plan_id === "demo";

  return (
    <div className="space-y-10">
      <div className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-violet-50/40 p-6 dark:border-emerald-900 dark:from-emerald-950/40 dark:to-violet-950/20">
        <p className="text-xs font-semibold uppercase tracking-widest text-emerald-700 dark:text-emerald-400">
          Mission plan ready
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50 sm:text-3xl">
          {track?.name ?? outputs.skill_gap?.role ?? "Your career roadmap"}
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          {plan.chosen_track_type} track
          {track ? ` · ${track.avg_starting_salary_band}` : ""}
          {isDemo ? " · Demo preview" : ""}
        </p>
      </div>

      <SharePlanBar plan={plan} />

      {plan.status === "completed" && weeks.length > 0 ? (
        <section id="checkin">
          <WeeklyCheckIn plan={plan} />
        </section>
      ) : null}

      <nav className="sticky top-14 z-10 -mx-1 overflow-x-auto border-b border-zinc-200 bg-white/90 py-2 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90">
        <ul className="flex gap-2 px-1 text-sm">
          {NAV.map((item) => (
            <li key={item.id}>
              <a
                href={`#${item.id}`}
                className="whitespace-nowrap rounded-full px-3 py-1.5 text-zinc-600 transition hover:bg-violet-100 hover:text-violet-800 dark:text-zinc-400 dark:hover:bg-violet-950 dark:hover:text-violet-200"
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <PlanSection
        id="track"
        title="Chosen track"
        description="Your selected path after the AI reality check (Agent 2)."
      >
        {track ? (
          <div className="rounded-2xl border border-zinc-200 p-5 dark:border-zinc-800">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <span className="text-xs font-semibold uppercase text-violet-600">
                  {track.type}
                </span>
                <h3 className="mt-1 text-lg font-semibold">{track.name}</h3>
              </div>
              {track.ai_risk_tier ? (
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    RISK_TIER_STYLES[track.ai_risk_tier]?.badge ??
                    RISK_TIER_STYLES[3].badge
                  }`}
                >
                  Tier {track.ai_risk_tier} ·{" "}
                  {track.ai_risk_label ?? RISK_TIER_STYLES[track.ai_risk_tier].label}
                </span>
              ) : null}
            </div>

            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-xs text-zinc-500">Salary band</dt>
                <dd className="font-medium">{track.avg_starting_salary_band}</dd>
              </div>
              <div>
                <dt className="text-xs text-zinc-500">Time to first offer</dt>
                <dd className="font-medium">
                  ~{track.time_to_job_estimate_months} months
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-xs text-zinc-500">Why this track</dt>
                <dd className="text-zinc-700 dark:text-zinc-300">
                  {track.why_recommended}
                </dd>
              </div>
            </dl>

            {track.honest_warning ? (
              <p className="mt-4 rounded-lg border border-amber-200/80 bg-amber-50/80 px-3 py-2 text-sm text-amber-900 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-200">
                ⚠ {track.honest_warning}
              </p>
            ) : null}

            <div className="mt-4 flex flex-wrap gap-2">
              {track.replaces.length > 0 ? (
                <TagGroup label="AI replaces" items={track.replaces} tone="orange" />
              ) : null}
              {track.amplifies.length > 0 ? (
                <TagGroup label="AI amplifies" items={track.amplifies} tone="sky" />
              ) : null}
            </div>

            {track.evolved_role_2029 ? (
              <p className="mt-3 text-sm">
                <span className="font-medium text-zinc-700 dark:text-zinc-300">
                  Evolved role (2029):{" "}
                </span>
                {track.evolved_role_2029}
              </p>
            ) : null}

            {track.survival_skills.length > 0 ? (
              <div className="mt-3">
                <p className="text-xs font-medium text-zinc-500">Survival skills</p>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {track.survival_skills.map((s) => (
                    <span
                      key={s}
                      className="rounded-md bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            {track.top_hiring_companies.length > 0 ? (
              <p className="mt-3 text-xs text-zinc-500">
                Hiring: {track.top_hiring_companies.join(" · ")}
              </p>
            ) : null}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">Track details unavailable.</p>
        )}
      </PlanSection>

      <PlanSection
        id="disruption"
        title="Disruption briefing"
        description="Agent 2 — how AI changes this career path in India."
      >
        {briefing ? (
          <div className="space-y-4 rounded-2xl border border-zinc-200 p-5 dark:border-zinc-800">
            <p className="leading-relaxed text-zinc-700 dark:text-zinc-300">
              {briefing.summary}
            </p>
            {briefing.do_not_pursue_callouts.length > 0 ? (
              <div>
                <p className="text-xs font-semibold uppercase text-amber-700 dark:text-amber-400">
                  Do not pursue
                </p>
                <ul className="mt-2 space-y-1.5 text-sm text-amber-900 dark:text-amber-200">
                  {briefing.do_not_pursue_callouts.map((line) => (
                    <li key={line}>· {line}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">No briefing available.</p>
        )}
      </PlanSection>

      <PlanSection
        id="gaps"
        title="Skill gaps"
        description="Agent 3 — your levels vs JD demand for this role."
      >
        {gaps.length > 0 ? (
          <div className="overflow-x-auto rounded-2xl border border-zinc-200 dark:border-zinc-800">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500 dark:border-zinc-800 dark:bg-zinc-900">
                <tr>
                  <th className="px-4 py-3 font-medium">Skill</th>
                  <th className="px-4 py-3 font-medium">You</th>
                  <th className="px-4 py-3 font-medium">Required</th>
                  <th className="px-4 py-3 font-medium">JD demand</th>
                  <th className="px-4 py-3 font-medium">Weeks</th>
                  <th className="px-4 py-3 font-medium">Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {gaps.map((g) => (
                  <tr key={g.name} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-900/30">
                    <td className="px-4 py-3 font-medium">{g.name}</td>
                    <td className="px-4 py-3">{g.current_level}/5</td>
                    <td className="px-4 py-3">{g.required_level}/5</td>
                    <td className="px-4 py-3">{g.demand_frequency_pct}%</td>
                    <td className="px-4 py-3">{g.weeks_to_bridge}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_STYLES[g.priority]}`}
                      >
                        {g.priority}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-zinc-500">No skill gaps computed yet.</p>
        )}
      </PlanSection>

      <PlanSection
        id="weeks"
        title="Week-by-week plan"
        description={`Agent 4 — ${outputs.learning_path?.total_weeks ?? weeks.length} weeks aligned to your hours/day and budget.`}
      >
        {weeks.length > 0 ? (
          <div className="space-y-2">
            {weeks.map((w) => (
              <div
                key={w.week}
                className={`rounded-xl border px-4 py-3 ${
                  w.checkpoint
                    ? "border-violet-300 bg-violet-50/50 dark:border-violet-800 dark:bg-violet-950/30"
                    : "border-zinc-200 dark:border-zinc-800"
                }`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-zinc-900 dark:text-zinc-50">
                    Week {w.week}
                  </span>
                  <span className="text-zinc-500">· {w.focus_skill}</span>
                  <span className="text-xs text-zinc-400">{w.hours}h</span>
                  {w.checkpoint ? (
                    <span className="rounded-full bg-violet-600 px-2 py-0.5 text-xs font-medium text-white">
                      Checkpoint
                    </span>
                  ) : null}
                </div>
                <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                  {w.mini_task}
                </p>
                {w.resources.length > 0 ? (
                  <ul className="mt-2 text-xs text-violet-700 dark:text-violet-300">
                    {w.resources.map((r) => (
                      <li key={r}>· {r}</li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">Learning path not generated yet.</p>
        )}
      </PlanSection>

      <PlanSection
        id="projects"
        title="Portfolio projects"
        description="Agent 5 — JD-aligned builds from Beginner to Capstone."
      >
        {projects.length > 0 ? (
          <ul className="space-y-4">
            {projects.map((p) => (
              <li
                key={p.name}
                className="rounded-2xl border border-zinc-200 p-5 dark:border-zinc-800"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold text-zinc-900 dark:text-zinc-50">
                    {p.name}
                  </h3>
                  <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium dark:bg-zinc-800">
                    {p.difficulty}
                  </span>
                  <span className="text-xs text-zinc-500">~{p.hours_estimate}h</span>
                </div>
                <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">
                  {p.problem_statement}
                </p>
                <dl className="mt-3 grid gap-2 text-xs text-zinc-600 sm:grid-cols-2 dark:text-zinc-400">
                  <div>
                    <dt className="font-medium text-zinc-500">Data / API</dt>
                    <dd>{p.dataset_or_api ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-zinc-500">Expected output</dt>
                    <dd>{p.expected_output}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="font-medium text-zinc-500">Stack</dt>
                    <dd>{p.tech_stack.join(" · ")}</dd>
                  </div>
                </dl>
                <p className="mt-3 rounded-lg bg-zinc-50 px-3 py-2 text-sm italic text-zinc-700 dark:bg-zinc-900 dark:text-zinc-300">
                  Resume: {p.resume_bullet}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-500">No projects generated yet.</p>
        )}
      </PlanSection>

      <PlanSection
        id="certs"
        title="Certifications"
        description="JD-backed picks (≥15% mention or proven callback boost) — and what not to buy."
      >
        {certs && certs.recommended.length > 0 ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">
                Recommended
              </h3>
              <ul className="mt-3 space-y-3">
                {certs.recommended.map((c) => (
                  <li
                    key={c.name}
                    className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-4 dark:border-emerald-900 dark:bg-emerald-950/30"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <h4 className="font-semibold text-zinc-900 dark:text-zinc-50">
                        {c.name}
                      </h4>
                      <span className="text-xs text-zinc-500">~{c.hours}h</span>
                    </div>
                    <p className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">
                      {c.provider} · {c.cost}
                    </p>
                    <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">{c.why}</p>
                  </li>
                ))}
              </ul>
            </div>
            {certs.skip.length > 0 ? (
              <div>
                <h3 className="text-sm font-semibold text-red-800 dark:text-red-300">
                  Do not buy
                </h3>
                <ul className="mt-3 space-y-2">
                  {certs.skip.map((s) => (
                    <li
                      key={s.name}
                      className="rounded-xl border border-red-200 bg-red-50/40 px-4 py-3 text-sm dark:border-red-900 dark:bg-red-950/20"
                    >
                      <p className="font-medium text-zinc-900 dark:text-zinc-50">{s.name}</p>
                      <p className="mt-1 text-zinc-600 dark:text-zinc-400">{s.why_skip}</p>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">No certification guidance yet.</p>
        )}
      </PlanSection>

      <PlanSection
        id="phase2"
        title="Portfolio & outreach"
        description="GitHub README, site copy, hosting pick, 12-week LinkedIn calendar, and connection templates."
      >
        {portfolio ? (
          <div className="space-y-8">
            <div>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                GitHub README
              </h3>
              <pre className="mt-2 max-h-72 overflow-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-xs leading-relaxed text-zinc-800 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
                {portfolio.github_readme_md}
              </pre>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                Portfolio site sections
              </h3>
              <div className="mt-3 space-y-3">
                {portfolio.portfolio_site_sections.map((s) => (
                  <details
                    key={s.section}
                    className="rounded-xl border border-zinc-200 dark:border-zinc-800"
                  >
                    <summary className="cursor-pointer px-4 py-3 text-sm font-medium capitalize text-zinc-900 dark:text-zinc-50">
                      {s.section}
                    </summary>
                    <p className="whitespace-pre-wrap border-t border-zinc-200 px-4 py-3 text-sm text-zinc-700 dark:border-zinc-800 dark:text-zinc-300">
                      {s.content}
                    </p>
                  </details>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-violet-200 bg-violet-50/50 p-4 text-sm dark:border-violet-900 dark:bg-violet-950/30">
              <p className="font-semibold text-violet-900 dark:text-violet-200">Hosting</p>
              <p className="mt-1 text-zinc-700 dark:text-zinc-300">
                {portfolio.hosting_suggestion}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                LinkedIn calendar (12 weeks · 4 posts/week)
              </h3>
              <div className="mt-3 space-y-2">
                {Array.from({ length: 12 }, (_, i) => i + 1).map((week) => {
                  const weekPosts = portfolio.linkedin_calendar.filter(
                    (p) => p.week === week,
                  );
                  return (
                    <details
                      key={week}
                      className="rounded-xl border border-zinc-200 dark:border-zinc-800"
                    >
                      <summary className="cursor-pointer px-4 py-2 text-sm font-medium text-zinc-900 dark:text-zinc-50">
                        Week {week}
                      </summary>
                      <ul className="space-y-3 border-t border-zinc-200 px-4 py-3 dark:border-zinc-800">
                        {weekPosts.map((post) => (
                          <li key={`${week}-${post.post_type}`}>
                            <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium capitalize dark:bg-zinc-800">
                              {post.post_type}
                            </span>
                            <pre className="mt-2 whitespace-pre-wrap text-xs text-zinc-700 dark:text-zinc-300">
                              {post.template}
                            </pre>
                          </li>
                        ))}
                      </ul>
                    </details>
                  );
                })}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                Connection request templates
              </h3>
              <ol className="mt-3 list-decimal space-y-3 pl-5 text-sm text-zinc-700 dark:text-zinc-300">
                {portfolio.connection_request_templates.map((t) => (
                  <li key={t.slice(0, 40)}>{t}</li>
                ))}
              </ol>
            </div>
          </div>
        ) : (
          <p className="text-sm text-zinc-500">Portfolio assets not generated yet.</p>
        )}
      </PlanSection>
    </div>
  );
}

function TagGroup({
  label,
  items,
  tone,
}: {
  label: string;
  items: string[];
  tone: "orange" | "sky";
}) {
  const cls =
    tone === "orange"
      ? "bg-orange-100 text-orange-900 dark:bg-orange-950 dark:text-orange-300"
      : "bg-sky-100 text-sky-900 dark:bg-sky-950 dark:text-sky-300";
  return (
    <div>
      <p className="text-xs font-medium text-zinc-500">{label}</p>
      <div className="mt-1 flex flex-wrap gap-1">
        {items.map((item) => (
          <span key={item} className={`rounded-md px-2 py-0.5 text-xs ${cls}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function ComingSoonCard({
  emoji,
  title,
  subtitle,
}: {
  emoji: string;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-zinc-300 bg-zinc-50/50 p-5 dark:border-zinc-700 dark:bg-zinc-900/30">
      <span className="text-2xl">{emoji}</span>
      <h3 className="mt-2 font-semibold text-zinc-900 dark:text-zinc-50">{title}</h3>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{subtitle}</p>
      <span className="mt-3 inline-block rounded-full bg-zinc-200 px-3 py-1 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
        Coming soon
      </span>
    </div>
  );
}
