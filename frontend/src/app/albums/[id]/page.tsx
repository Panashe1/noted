import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";

import { api, ApiError, type Album } from "@/lib/api";

type Props = { params: Promise<{ id: string }> };

async function getAlbum(id: string): Promise<Album> {
  try {
    return await api.album(id, { next: { revalidate: 3600 } });
  } catch (err) {
    if (err instanceof ApiError && (err.status === 404 || err.status === 422)) notFound();
    throw err;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const album = await getAlbum(id);
  return { title: `${album.title} by ${album.artist.name}` };
}

export default async function AlbumPage({ params }: Props) {
  const { id } = await params;
  const album = await getAlbum(id);

  const facts = [
    album.release_date && ["Released", album.release_date],
    album.genre && ["Genre", album.genre],
    album.track_count && ["Tracks", String(album.track_count)],
  ].filter((f): f is [string, string] => Boolean(f));

  return (
    <article className="grid gap-8 md:grid-cols-[280px_1fr]">
      <div className="relative aspect-square overflow-hidden rounded-lg border border-border bg-surface">
        {album.artwork_url ? (
          <Image
            src={album.artwork_url}
            alt={`${album.title} cover`}
            fill
            priority
            sizes="280px"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-6xl text-muted">♪</div>
        )}
      </div>

      <div className="space-y-6">
        <header>
          <h1 className="text-3xl font-semibold tracking-tight">{album.title}</h1>
          <p className="text-lg text-muted">{album.artist.name}</p>
        </header>

        {facts.length > 0 && (
          <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-1 text-sm">
            {facts.map(([label, value]) => (
              <div key={label} className="contents">
                <dt className="text-muted">{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        )}

        <div className="rounded-lg border border-dashed border-border p-6 text-sm text-muted">
          Ratings and reviews land in the next milestone.
        </div>
      </div>
    </article>
  );
}
