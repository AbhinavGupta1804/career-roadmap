import Link from "next/link";

import { AuthButton } from "@/components/auth/auth-button";

export function SiteHeader() {
  return (
    <header className="border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
        <Link
          href="/"
          className="text-sm font-semibold tracking-tight text-zinc-900 dark:text-zinc-50"
        >
          Career Roadmap
        </Link>
        <nav className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-400">
          <AuthButton />
          <Link
            href="/intake"
            className="rounded-full bg-zinc-900 px-4 py-1.5 font-medium text-white transition hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
          >
            Start intake
          </Link>
        </nav>
      </div>
    </header>
  );
}
