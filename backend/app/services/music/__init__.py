from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from app.core.deps import DbSession
from app.services.music.base import MusicProvider
from app.services.music.catalog import CatalogService
from app.services.music.itunes import ITunesProvider

_provider = ITunesProvider(
    country=settings.itunes_country, cache_ttl_seconds=settings.itunes_cache_ttl_seconds
)


def get_provider() -> MusicProvider:
    return _provider


async def close_provider() -> None:
    await _provider.close()


def get_catalog(
    db: DbSession, provider: Annotated[MusicProvider, Depends(get_provider)]
) -> CatalogService:
    return CatalogService(db, provider)


Catalog = Annotated[CatalogService, Depends(get_catalog)]

__all__ = ["Catalog", "CatalogService", "MusicProvider", "close_provider", "get_provider"]
