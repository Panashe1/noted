import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { api, ApiError, type PublicUser } from "@/lib/api";

type Props = { params: Promise<{ username: string }> };

async function getUser(username: string): Promise<PublicUser> {
  try {
    return await api.user(username, { cache: "no-store" });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { username } = await params;
  const user = await getUser(username);
  return { title: user.display_name ?? `@${user.username}` };
}

export default async function ProfilePage({ params }: Props) {
  const { username } = await params;
  const user = await getUser(username);
  const joined = new Date(user.created_at).toLocaleDateString("en-GB", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="space-y-6">
      <header className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-accent-muted text-2xl">
          {user.username[0].toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-semibold">{user.display_name ?? user.username}</h1>
          <p className="text-sm text-muted">
            @{user.username} · joined {joined}
          </p>
        </div>
      </header>
      {user.bio && <p className="max-w-prose">{user.bio}</p>}
      <div className="rounded-lg border border-dashed border-border p-6 text-sm text-muted">
        Diary, reviews and lists will show up here.
      </div>
    </div>
  );
}
