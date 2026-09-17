"use client";

import Link from "next/link";
import { useState } from "react";

import { StarInput } from "@/components/star-input";
import { ApiError, type Review } from "@/lib/api";
import { useDeleteReview, useMe, useMyReview, useSaveReview } from "@/lib/hooks";

const BODY_MAX_LENGTH = 10_000;

function Skeleton() {
  return <div className="h-32 animate-pulse rounded-lg bg-surface" />;
}

export function ReviewForm({ albumId }: { albumId: string }) {
  const { data: me, isPending: mePending } = useMe();
  const { data: mine, isPending: minePending } = useMyReview(albumId, Boolean(me));

  if (mePending) return <Skeleton />;

  if (!me) {
    return (
      <div className="rounded-lg border border-border bg-surface p-4 text-sm text-muted">
        <Link href="/login" className="text-accent hover:underline">
          Log in
        </Link>{" "}
        to rate and review this album.
      </div>
    );
  }

  if (minePending) return <Skeleton />;

  // Keying on the saved review means React remounts the fields with fresh defaults
  // whenever the stored review changes, instead of syncing props into state in an effect.
  return (
    <ReviewFields
      key={`${mine?.id ?? "new"}:${mine?.updated_at ?? ""}`}
      albumId={albumId}
      initial={mine ?? null}
    />
  );
}

function ReviewFields({ albumId, initial }: { albumId: string; initial: Review | null }) {
  const [rating, setRating] = useState(initial?.rating ?? 0);
  const [body, setBody] = useState(initial?.body ?? "");
  const [listenedAt, setListenedAt] = useState(initial?.listened_at ?? "");
  const [spoilers, setSpoilers] = useState(initial?.contains_spoilers ?? false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const save = useSaveReview(albumId);
  const remove = useDeleteReview(albumId);

  const submitError =
    save.error instanceof ApiError ? save.error.detail : (save.error?.message ?? null);

  function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (rating === 0) {
      setValidationError("Pick a rating before saving.");
      return;
    }
    setValidationError(null);
    save.mutate({
      rating,
      body: body.trim() || null,
      listened_at: listenedAt || null,
      contains_spoilers: spoilers,
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium">{initial ? "Your review" : "Rate this album"}</h3>
        {initial && (
          <button
            type="button"
            onClick={() => remove.mutate()}
            disabled={remove.isPending}
            className="text-xs text-muted hover:text-danger disabled:opacity-50"
          >
            Delete
          </button>
        )}
      </div>

      <StarInput value={rating} onChange={setRating} />

      <textarea
        value={body}
        onChange={(event) => setBody(event.target.value)}
        maxLength={BODY_MAX_LENGTH}
        rows={4}
        placeholder="What did you make of it? (optional)"
        className="w-full resize-y rounded-md border border-border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted focus:border-accent"
      />

      <div className="flex flex-wrap items-center gap-4 text-sm">
        <label className="flex items-center gap-2">
          <span className="text-muted">Listened on</span>
          <input
            type="date"
            value={listenedAt}
            max={new Date().toISOString().slice(0, 10)}
            onChange={(event) => setListenedAt(event.target.value)}
            className="rounded-md border border-border bg-background px-2 py-1 outline-none focus:border-accent"
          />
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={spoilers}
            onChange={(event) => setSpoilers(event.target.checked)}
            className="accent-accent"
          />
          <span className="text-muted">Contains spoilers</span>
        </label>
      </div>

      {validationError && <p className="text-sm text-danger">{validationError}</p>}
      {submitError && <p className="text-sm text-danger">{submitError}</p>}

      <button
        type="submit"
        disabled={save.isPending}
        className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:opacity-90 disabled:opacity-60"
      >
        {save.isPending ? "Saving…" : initial ? "Update review" : "Save review"}
      </button>
    </form>
  );
}
