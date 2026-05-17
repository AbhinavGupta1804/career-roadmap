"use client";

import { useEffect, useState } from "react";

import {
  createClient,
  isSupabaseAuthConfigured,
} from "@/lib/supabase/client";

export function AuthButton() {
  const [email, setEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isSupabaseAuthConfigured()) return;

    const supabase = createClient();

    void supabase.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setEmail(session?.user?.email ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (!isSupabaseAuthConfigured()) {
    return null;
  }

  async function signInWithGoogle() {
    setLoading(true);
    try {
      const supabase = createClient();
      const redirectTo = `${window.location.origin}/auth/callback`;
      await supabase.auth.signInWithOAuth({
        provider: "google",
        options: { redirectTo },
      });
    } finally {
      setLoading(false);
    }
  }

  async function signOut() {
    setLoading(true);
    try {
      const supabase = createClient();
      await supabase.auth.signOut();
      setEmail(null);
    } finally {
      setLoading(false);
    }
  }

  if (email) {
    return (
      <div className="flex items-center gap-2">
        <span className="hidden max-w-[140px] truncate text-xs text-zinc-500 sm:inline">
          {email}
        </span>
        <button
          type="button"
          onClick={() => void signOut()}
          disabled={loading}
          className="rounded-full border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300"
        >
          Sign out
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => void signInWithGoogle()}
      disabled={loading}
      className="rounded-full border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300"
    >
      {loading ? "…" : "Sign in with Google"}
    </button>
  );
}
