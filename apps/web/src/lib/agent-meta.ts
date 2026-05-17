export type AgentMeta = {
  id: string;
  title: string;
  subtitle: string;
  emoji: string;
};

/** Display order for the “reel moment” (§5). */
export const AGENT_REEL: AgentMeta[] = [
  {
    id: "career_path_picker",
    title: "Career Path Picker",
    subtitle: "3 tracks tuned to your profile",
    emoji: "🧭",
  },
  {
    id: "ai_reality_check",
    title: "AI Reality Check",
    subtitle: "Disruption tiers & honest warnings",
    emoji: "⚡",
  },
  {
    id: "skill_gap_analyzer",
    title: "Skill Gap Analyzer",
    subtitle: "You vs real JD demand",
    emoji: "📊",
  },
  {
    id: "learning_path_generator",
    title: "Learning Path Generator",
    subtitle: "Week-by-week roadmap",
    emoji: "📅",
  },
  {
    id: "project_ideator",
    title: "Project Ideator",
    subtitle: "Portfolio projects with bullets",
    emoji: "🛠️",
  },
  {
    id: "certification_advisor",
    title: "Certification Advisor",
    subtitle: "What to skip vs pursue",
    emoji: "🎓",
  },
  {
    id: "portfolio_builder",
    title: "Portfolio Builder",
    subtitle: "GitHub, site & LinkedIn plan",
    emoji: "✨",
  },
];

export const TRACK_TYPE_ORDER = ["Stretch", "Realistic", "Safe"] as const;

export const RISK_TIER_STYLES: Record<
  number,
  { label: string; badge: string; ring: string }
> = {
  1: {
    label: "Tailwind",
    badge:
      "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    ring: "ring-emerald-500/40",
  },
  2: {
    label: "Augmented",
    badge: "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300",
    ring: "ring-sky-500/40",
  },
  3: {
    label: "Partial risk",
    badge: "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-300",
    ring: "ring-amber-500/40",
  },
  4: {
    label: "Heavy disruption",
    badge:
      "bg-orange-100 text-orange-900 dark:bg-orange-950 dark:text-orange-300",
    ring: "ring-orange-500/40",
  },
  5: {
    label: "Sunset",
    badge: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
    ring: "ring-red-500/40",
  },
};
