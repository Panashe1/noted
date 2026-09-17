import Image from "next/image";
import Link from "next/link";

import type { Album } from "@/lib/api";

export function AlbumCard({ album }: { album: Album }) {
  const year = album.release_date?.slice(0, 4);
  return (
    <Link
      href={`/albums/${album.id}`}
      className="group block overflow-hidden rounded-lg border border-border bg-surface transition hover:border-muted"
    >
      <div className="relative aspect-square bg-surface-hover">
        {album.artwork_url ? (
          <Image
            src={album.artwork_url}
            alt={`${album.title} cover`}
            fill
            sizes="(max-width: 640px) 50vw, 200px"
            className="object-cover transition group-hover:scale-[1.02]"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-4xl text-muted">♪</div>
        )}
      </div>
      <div className="p-3">
        <p className="truncate text-sm font-medium" title={album.title}>
          {album.title}
        </p>
        <p className="truncate text-xs text-muted">
          {album.artist.name}
          {year ? ` · ${year}` : ""}
        </p>
      </div>
    </Link>
  );
}
