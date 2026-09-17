"""Provider-agnostic music metadata contract.

Anything that can search for albums and fetch one by its provider id can back the catalog.
Today that's iTunes; Apple Music or MusicBrainz would be a second adapter, not a rewrite.
"""

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ProviderArtist:
    name: str
    provider_id: int | None = None


@dataclass(frozen=True, slots=True)
class ProviderAlbum:
    provider_id: int
    title: str
    artist: ProviderArtist
    artwork_url: str | None = None
    release_date: date | None = None
    genre: str | None = None
    track_count: int | None = None
    upc: str | None = None


class MusicProvider(Protocol):
    name: str

    async def search_albums(self, query: str, *, limit: int = 20) -> list[ProviderAlbum]: ...

    async def get_album(self, provider_id: int) -> ProviderAlbum | None: ...
