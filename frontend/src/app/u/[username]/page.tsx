import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Stars } from "@/components/stars";
import { api, ApiError, type PublicUser, type ReviewWithAlbum } from "@/lib/api";

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

function ReviewRow({ review }: { review: ReviewWithAlbum }) {
  const { album } = review;
  return (
    <li className="flex gap-4 border-b border-border py-4 last:border-b-0">
      <Link
        href={`/albums/${album.id}`}
        className="relative h-16 w-16 shrink-0 overflow-hidden rounded border border-border bg-surface"
      >
        {album.artwork_url ? (
          <Image
            src={album.artwork_url}
            alt={`${album.title} cover`}
            fill
            sizes="64px"
            className="object-cover"
          />
        ) : (
          <span className="flex h-full items-center justify-center text-xl text-muted">♪</span>
        )}
      </Link>
      <div className="min-w-0 flex-1">
        <Link href={`/albums/${album.id}`} className="font-medium hover:text-accent">
          {album.title}
        </Link>
        <p className="truncate text-sm text-muted">{album.artist.name}</p>
        <div className="mt-1 flex items-center gap-2">
          <Stars value={review.rating} />
          {review.contains_spoilers && <span className="text-xs text-muted">spoilers</span>}
        </div>
        {review.body && !review.contains_spoilers && (
          <p className="mt-2 line-clamp-3 text-sm whitespace-pre-line">{review.body}</p>
        )}
      </div>
    </li>
  );
}

export default async function ProfilePage({ params }: Props) {
  const { username } = await params;
  const user = await getUser(username);
  const reviews = await api.userReviews(user.username);
  const joined = new Date(user.created_at).toLocaleDateString("en-GB", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="space-y-8">
      <header className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-accent-muted text-2xl">
          {user.username[0].toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-semibold">{user.display_name ?? user.username}</h1>
          <p className="text-sm text-muted">
            @{user.username} · joined {joined} · {reviews.total}{" "}
            {reviews.total === 1 ? "review" : "reviews"}
          </p>
        </div>
      </header>

      {user.bio && <p className="max-w-prose">{user.bio}</p>}

      <section>
        <h2 className="border-b border-border pb-2 text-sm font-medium tracking-wide text-muted uppercase">
          Recent reviews
        </h2>
        {reviews.items.length === 0 ? (
          <p className="py-4 text-sm text-muted">No reviews yet.</p>
        ) : (
          <ul>
            {reviews.items.map((review) => (
              <ReviewRow key={review.id} review={review} />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
