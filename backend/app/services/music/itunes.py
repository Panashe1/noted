"""Adapter for the keyless iTunes Search API.

Notes:
- No auth. Roughly 20 requests/minute/IP, so every response is cached (see app.core.cache).
- collectionId is the same id the Apple Music API uses, which keeps a future upgrade painless.
- artworkUrl100 can be rewritten to larger sizes; 600px is a good default for grids.
"""

import json
import logging
from datetime import date, datetime
from typing import Any

import httpx

from app.core.cache import cache
from app.services.music.base import ProviderAlbum, ProviderArtist

log = logging.getLogger(__name__)

SEARCH_URL = "https://itunes.apple.com/search"
LOOKUP_URL = "https://itunes.apple.com/lookup"


class ITunesProvider:
    name = "itunes"

    def __init__(
        self,
        country: str,
        cache_ttl_seconds: int,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._country = country
        self._ttl = cache_ttl_seconds
        self._client = client or httpx.AsyncClient(
            timeout=10.0, headers={"User-Agent": "noted/0.1 (+https://github.com)"}
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def search_albums(self, query: str, *, limit: int = 20) -> list[ProviderAlbum]:
        params: dict[str, Any] = {
            "term": query,
            "media": "music",
            "entity": "album",
            "limit": limit,
            "country": self._country,
        }
        raw = await self._get(SEARCH_URL, params)
        return [album for album in map(parse_album, raw) if album is not None]

    async def get_album(self, provider_id: int) -> ProviderAlbum | None:
        raw = await self._get(
            LOOKUP_URL, {"id": provider_id, "entity": "album", "country": self._country}
        )
        for item in raw:
            album = parse_album(item)
            if album is not None and album.provider_id == provider_id:
                return album
        return None

    async def _get(self, url: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        key = f"itunes:{url.rsplit('/', 1)[-1]}:{json.dumps(params, sort_keys=True)}"
        cached = await cache.get(key)
        if cached is not None:
            return list(cached)
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        results: list[dict[str, Any]] = response.json().get("results", [])
        await cache.set(key, results, self._ttl)
        return results


def parse_album(item: dict[str, Any]) -> ProviderAlbum | None:
    if item.get("wrapperType") != "collection" or item.get("collectionType") != "Album":
        return None
    try:
        artist_id = item.get("artistId")
        return ProviderAlbum(
            provider_id=int(item["collectionId"]),
            title=str(item["collectionName"]),
            artist=ProviderArtist(
                name=str(item["artistName"]),
                provider_id=int(artist_id) if artist_id is not None else None,
            ),
            artwork_url=upscale_artwork(item.get("artworkUrl100")),
            release_date=parse_release_date(item.get("releaseDate")),
            genre=item.get("primaryGenreName"),
            track_count=item.get("trackCount"),
        )
    except (KeyError, TypeError, ValueError):
        log.warning("Skipping malformed iTunes item: %s", item.get("collectionId"))
        return None


def upscale_artwork(url: str | None, size: int = 600) -> str | None:
    if not url:
        return None
    return url.replace("100x100bb", f"{size}x{size}bb")


def parse_release_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None
