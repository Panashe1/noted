"use client";

import { useState } from "react";

import { AlbumCard } from "@/components/album-card";
import { useAlbumSearch, useDebouncedValue } from "@/lib/hooks";

export function AlbumSearch() {
  const [input, setInput] = useState("");
  const query = useDebouncedValue(input, 300);
  const { data, isFetching, error } = useAlbumSearch(query);

  return (
    <section className="space-y-6">
      <div className="relative">
        <input
          type="search"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Search for an album or artist…"
          autoFocus
          className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-base outline-none placeholder:text-muted focus:border-accent"
        />
        {isFetching && (
          <span className="absolute top-1/2 right-4 -translate-y-1/2 text-xs text-muted">
            searching…
          </span>
        )}
      </div>

      {error && <p className="text-sm text-danger">Search failed: {error.message}</p>}

      {data && data.results.length === 0 && (
        <p className="text-sm text-muted">No albums found for “{data.query}”.</p>
      )}

      {data && data.results.length > 0 && (
        <>
          <p className="text-xs text-muted">
            {data.results.length} result{data.results.length === 1 ? "" : "s"} · source: {data.source}
          </p>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {data.results.map((album) => (
              <AlbumCard key={album.id} album={album} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
