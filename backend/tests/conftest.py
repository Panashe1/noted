from collections.abc import AsyncIterator

import pytest
from app.core.db import get_db
from app.main import app
from app.models import Base
from app.services.music import get_provider
from app.services.music.base import ProviderAlbum, ProviderArtist
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


class FakeProvider:
    """Deterministic stand-in for iTunes so tests never touch the network."""

    name = "fake"

    def __init__(self) -> None:
        self.albums = [
            ProviderAlbum(
                provider_id=1001,
                title="In Rainbows",
                artist=ProviderArtist(name="Radiohead", provider_id=657515),
                artwork_url="https://example.invalid/in-rainbows.jpg",
                genre="Alternative",
                track_count=10,
            ),
            ProviderAlbum(
                provider_id=1002,
                title="Kid A",
                artist=ProviderArtist(name="Radiohead", provider_id=657515),
                genre="Alternative",
                track_count=10,
            ),
        ]
        self.search_calls = 0

    async def search_albums(self, query: str, *, limit: int = 20) -> list[ProviderAlbum]:
        self.search_calls += 1
        needle = query.lower()
        return [
            album
            for album in self.albums
            if needle in album.title.lower() or needle in album.artist.name.lower()
        ][:limit]

    async def get_album(self, provider_id: int) -> ProviderAlbum | None:
        return next((a for a in self.albums if a.provider_id == provider_id), None)


@pytest.fixture
def fake_provider() -> FakeProvider:
    return FakeProvider()


@pytest.fixture
async def client(fake_provider: FakeProvider) -> AsyncIterator[AsyncClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db() -> AsyncIterator[object]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_provider] = lambda: fake_provider

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http

    app.dependency_overrides.clear()
    await engine.dispose()
