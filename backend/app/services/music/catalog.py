"""Local-first album catalog.

Search hits our own database first. Only when that comes up short do we ask the provider,
and everything the provider returns is persisted so the next search is served locally.
That keeps us well under the iTunes rate limit as the catalog grows.
"""

import logging
import uuid

import httpx
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.music import Album, Artist
from app.schemas.music import SearchSource
from app.services.music.base import MusicProvider, ProviderAlbum, ProviderArtist

log = logging.getLogger(__name__)

LOCAL_RESULTS_SUFFICIENT = 8


class CatalogService:
    def __init__(self, db: AsyncSession, provider: MusicProvider) -> None:
        self._db = db
        self._provider = provider

    async def search(self, query: str, limit: int = 20) -> tuple[list[Album], SearchSource]:
        local = await self._search_local(query, limit)
        if len(local) >= LOCAL_RESULTS_SUFFICIENT:
            return local, "local"

        try:
            remote = await self._provider.search_albums(query, limit=limit)
        except httpx.HTTPError as exc:
            log.warning("Provider %s search failed: %s", self._provider.name, exc)
            return local, "local"

        imported = [await self._upsert_album(album) for album in remote]
        await self._db.commit()

        seen: set[uuid.UUID] = set()
        merged: list[Album] = []
        for album in [*local, *imported]:
            if album.id not in seen:
                seen.add(album.id)
                merged.append(album)
        source: SearchSource = "mixed" if local else "itunes"
        return merged[:limit], source

    async def get_by_id(self, album_id: uuid.UUID) -> Album | None:
        return await self._db.get(Album, album_id)

    async def get_by_apple_id(self, apple_id: int) -> Album | None:
        album = await self._db.scalar(select(Album).where(Album.apple_id == apple_id))
        if album is not None:
            return album
        remote = await self._provider.get_album(apple_id)
        if remote is None:
            return None
        album = await self._upsert_album(remote)
        await self._db.commit()
        return album

    async def _search_local(self, query: str, limit: int) -> list[Album]:
        # Every word in the query must appear in the title or the artist name, so
        # "radiohead in rainbows" matches title "In Rainbows" by artist "Radiohead".
        tokens = [_escape_like(token) for token in query.split()]
        if not tokens:
            return []
        conditions = [
            or_(
                Album.title.ilike(f"%{token}%", escape="\\"),
                Artist.name.ilike(f"%{token}%", escape="\\"),
            )
            for token in tokens
        ]
        stmt = (
            select(Album).join(Album.artist).where(*conditions).order_by(Album.title).limit(limit)
        )
        return list((await self._db.scalars(stmt)).unique().all())

    async def _upsert_album(self, remote: ProviderAlbum) -> Album:
        existing = await self._db.scalar(select(Album).where(Album.apple_id == remote.provider_id))
        if existing is not None:
            return existing

        artist = await self._get_or_create_artist(remote.artist)
        album = Album(
            title=remote.title,
            apple_id=remote.provider_id,
            upc=remote.upc,
            release_date=remote.release_date,
            artwork_url=remote.artwork_url,
            genre=remote.genre,
            track_count=remote.track_count,
        )
        try:
            async with self._db.begin_nested():
                self._db.add(album)
                album.artist = artist
                await self._db.flush()
        except IntegrityError:
            # A concurrent request imported the same album first. Use theirs.
            refetched = await self._db.scalar(
                select(Album).where(Album.apple_id == remote.provider_id)
            )
            if refetched is None:
                raise
            return refetched
        return album

    async def _get_or_create_artist(self, remote: ProviderArtist) -> Artist:
        if remote.provider_id is not None:
            stmt = select(Artist).where(Artist.apple_id == remote.provider_id)
        else:
            stmt = select(Artist).where(Artist.apple_id.is_(None), Artist.name == remote.name)
        artist = await self._db.scalar(stmt)
        if artist is not None:
            return artist
        artist = Artist(name=remote.name, apple_id=remote.provider_id)
        self._db.add(artist)
        await self._db.flush()
        return artist


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
