"use client";

import Link from "next/link";
import { useState } from "react";

import { Stars } from "@/components/stars";
import type { Review } from "@/lib/api";
import { useAlbumReviews } from "@/lib/hooks";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function ReviewBody({ review }: { review: Review }) {
  const [revealed, setRevealed] = useState(false);

  if (!review.body) return null;
  if (review.contains_spoilers && !revealed) {
    return (
      <button
        type="button"
        onClick={() => setRevealed(true)}
        className="mt-2 w-full rounded-md border border-dashed border-border px-3 py-2 text-left text-sm text-muted hover:border-accent hover:text-foreground"
      >
        This review mentions spoilers. Click to show.
      </button>
    );
  }
  return <p className="mt-2 text-sm whitespace-pre-line">{review.body}</p>;
}

function ReviewItem({ review }: { review: Review }) {
  return (
    <li className="border-b border-border py-4 last:border-b-0">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <Link href={`/u/${review.user.username}`} className="text-sm font-medium hover:text-accent">
          {review.user.display_name ?? review.user.username}
        </Link>
        <Stars value={review.rating} />
        {review.listened_at && (
          <span className="text-xs text-muted">listened {formatDate(review.listened_at)}</span>
        )}
      </div>
      <ReviewBody review={review} />
    </li>
  );
}

const PAGE_SIZE = 10;

export function ReviewList({ albumId }: { albumId: string }) {
  const [offset, setOffset] = useState(0);
  const { data, isPending, error } = useAlbumReviews(albumId, PAGE_SIZE, offset);

  if (isPending) return <p className="py-4 text-sm text-muted">Loading reviews…</p>;
  if (error) return <p className="py-4 text-sm text-danger">Could not load reviews.</p>;
  if (data.total === 0) {
    return <p className="py-4 text-sm text-muted">No reviews yet. Be the first.</p>;
  }

  const shown = offset + data.items.length;
  return (
    <div>
      <ul>
        {data.items.map((review) => (
          <ReviewItem key={review.id} review={review} />
        ))}
      </ul>
      {data.total > PAGE_SIZE && (
        <div className="flex items-center justify-between pt-4 text-sm">
          <button
            type="button"
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            disabled={offset === 0}
            className="text-muted hover:text-foreground disabled:opacity-40"
          >
            ← Newer
          </button>
          <span className="text-xs text-muted">
            {offset + 1}–{shown} of {data.total}
          </span>
          <button
            type="button"
            onClick={() => setOffset(offset + PAGE_SIZE)}
            disabled={shown >= data.total}
            className="text-muted hover:text-foreground disabled:opacity-40"
          >
            Older →
          </button>
        </div>
      )}
    </div>
  );
}
