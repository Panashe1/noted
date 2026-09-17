from httpx import AsyncClient

from tests.conftest import FakeProvider


async def test_search_imports_from_provider_then_serves_locally(
    client: AsyncClient, fake_provider: FakeProvider
) -> None:
    first = await client.get("/api/v1/albums/search", params={"q": "radiohead"})
    assert first.status_code == 200, first.text
    body = first.json()
    assert body["source"] == "itunes"
    titles = {album["title"] for album in body["results"]}
    assert titles == {"In Rainbows", "Kid A"}
    assert all(album["artist"]["name"] == "Radiohead" for album in body["results"])
    assert fake_provider.search_calls == 1

    # Second search still consults the provider (fewer than 8 local hits) but must not
    # create duplicate rows for albums it already imported.
    second = await client.get("/api/v1/albums/search", params={"q": "radiohead"})
    assert second.status_code == 200
    assert len(second.json()["results"]) == 2
    assert second.json()["source"] == "mixed"


async def test_album_detail_by_id_and_apple_id(client: AsyncClient) -> None:
    search = await client.get("/api/v1/albums/search", params={"q": "kid a"})
    album = search.json()["results"][0]

    by_id = await client.get(f"/api/v1/albums/{album['id']}")
    assert by_id.status_code == 200
    assert by_id.json()["title"] == "Kid A"

    by_apple = await client.get("/api/v1/albums/apple/1002")
    assert by_apple.status_code == 200
    assert by_apple.json()["id"] == album["id"]

    assert (await client.get("/api/v1/albums/apple/999")).status_code == 404


async def test_search_requires_query(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/albums/search")).status_code == 422


async def test_local_search_matches_words_across_title_and_artist(
    client: AsyncClient, fake_provider: FakeProvider
) -> None:
    await client.get("/api/v1/albums/search", params={"q": "radiohead"})
    fake_provider.albums = []  # provider now returns nothing; only local rows can match

    combined = await client.get("/api/v1/albums/search", params={"q": "radiohead kid a"})
    assert [a["title"] for a in combined.json()["results"]] == ["Kid A"]

    escaped = await client.get("/api/v1/albums/search", params={"q": "100%"})
    assert escaped.status_code == 200
    assert escaped.json()["results"] == []
