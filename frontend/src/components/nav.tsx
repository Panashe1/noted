"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useLogout, useMe } from "@/lib/hooks";

export function Nav() {
  const { data: me, isPending } = useMe();
  const logout = useLogout();
  const router = useRouter();

  return (
    <header className="border-b border-border bg-surface/60 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          <span className="text-accent">●</span> Noted
        </Link>

        <nav className="flex items-center gap-4 text-sm">
          {isPending ? (
            <span className="h-4 w-20 animate-pulse rounded bg-surface-hover" />
          ) : me ? (
            <>
              <Link href={`/u/${me.username}`} className="text-muted hover:text-foreground">
                @{me.username}
              </Link>
              <button
                type="button"
                onClick={() => logout.mutate(undefined, { onSuccess: () => router.push("/") })}
                className="text-muted hover:text-foreground"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-muted hover:text-foreground">
                Log in
              </Link>
              <Link
                href="/register"
                className="rounded-md bg-accent px-3 py-1.5 font-medium text-accent-foreground hover:opacity-90"
              >
                Join
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
