from datetime import date, timedelta

import pytest
from httpx import AsyncClient

ALICE = {"email": "alice@noted.dev", "username": "alice", "password": "correct-horse-battery"}
BOB = {"email": "bob@noted.dev", "username": "bob", "password": "correct-horse-battery"}


async def register(client: AsyncClient, who: dict[str, str]) -> None:
    response = await client.post("/api/v1/auth/register", json=who)
    assert response.status_code == 201, response.text


async def seed_album(client: AsyncClient, query: str = "in rainbows") -> str:
    """Import an album from the fake provider and return its id."""
    response = await client.get("/api/v1/albums/search", params={"q": query})
    assert response.status_code == 200, response.text
    album_id: str = response.json()["results"][0]["id"]
    return album_id


async def test_create_review_returns_201_and_converts_rating(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)

    response = await client.put(
        f"/api/v1/albums/{album_id}/review",
        json={"rating": 4.5, "body": "  Still unmatched.  ", "listened_at": "2026-09-01"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["rating"] == 4.5
    assert body["body"] == "Still unmatched."  # trimmed
    assert body["listened_at"] == "2026-09-01"
    assert body["contains_spoilers"] is False
    assert body["user"]["username"] == "alice"
    assert "email" not in body["user"]


async def test_second_put_updates_rather_than_duplicating(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)

    first = await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 3})
    assert first.status_code == 201

    second = await client.put(
        f"/api/v1/albums/{album_id}/review", json={"rating": 5, "body": "Grew on me."}
    )
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["rating"] == 5.0

    listing = await client.get(f"/api/v1/albums/{album_id}/reviews")
    assert listing.json()["total"] == 1


async def test_clearing_body_is_allowed(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 4, "body": "words"})

    cleared = await client.put(
        f"/api/v1/albums/{album_id}/review", json={"rating": 4, "body": "  "}
    )
    assert cleared.status_code == 200
    assert cleared.json()["body"] is None


@pytest.mark.parametrize("rating", [0, 0.25, 4.3, 5.5, -1])
async def test_rejects_ratings_off_the_half_star_scale(client: AsyncClient, rating: float) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    response = await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": rating})
    assert response.status_code == 422


async def test_rejects_future_listened_at(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = await client.put(
        f"/api/v1/albums/{album_id}/review", json={"rating": 4, "listened_at": tomorrow}
    )
    assert response.status_code == 422


async def test_review_requires_authentication(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    await client.post("/api/v1/auth/logout")

    response = await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 4})
    assert response.status_code == 401


async def test_review_on_unknown_album_is_404(client: AsyncClient) -> None:
    await register(client, ALICE)
    missing = "00000000-0000-0000-0000-000000000000"
    response = await client.put(f"/api/v1/albums/{missing}/review", json={"rating": 4})
    assert response.status_code == 404
    assert (await client.get(f"/api/v1/albums/{missing}/reviews")).status_code == 404


async def test_album_detail_carries_rating_aggregate(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)

    before = await client.get(f"/api/v1/albums/{album_id}")
    assert before.json()["average_rating"] is None
    assert before.json()["review_count"] == 0

    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 4.5})
    await client.post("/api/v1/auth/logout")
    await register(client, BOB)
    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 3})

    after = await client.get(f"/api/v1/albums/{album_id}")
    assert after.json()["review_count"] == 2
    assert after.json()["average_rating"] == 3.75  # mean of 4.5 and 3.0


async def test_own_review_endpoints(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)

    assert (await client.get(f"/api/v1/albums/{album_id}/review")).status_code == 404

    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 2.5})
    mine = await client.get(f"/api/v1/albums/{album_id}/review")
    assert mine.status_code == 200
    assert mine.json()["rating"] == 2.5

    deleted = await client.delete(f"/api/v1/albums/{album_id}/review")
    assert deleted.status_code == 204
    assert (await client.get(f"/api/v1/albums/{album_id}/review")).status_code == 404
    assert (await client.delete(f"/api/v1/albums/{album_id}/review")).status_code == 404

    detail = await client.get(f"/api/v1/albums/{album_id}")
    assert detail.json()["review_count"] == 0


async def test_one_user_cannot_touch_anothers_review(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 5})

    await client.post("/api/v1/auth/logout")
    await register(client, BOB)

    # Bob deleting "his" review on the same album must not remove Alice's.
    assert (await client.delete(f"/api/v1/albums/{album_id}/review")).status_code == 404
    listing = await client.get(f"/api/v1/albums/{album_id}/reviews")
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["user"]["username"] == "alice"


async def test_album_review_listing_paginates(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 4})
    await client.post("/api/v1/auth/logout")
    await register(client, BOB)
    await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 2})

    first = await client.get(f"/api/v1/albums/{album_id}/reviews", params={"limit": 1})
    assert first.json()["total"] == 2
    assert len(first.json()["items"]) == 1
    assert first.json()["limit"] == 1

    second = await client.get(
        f"/api/v1/albums/{album_id}/reviews", params={"limit": 1, "offset": 1}
    )
    assert len(second.json()["items"]) == 1

    # The two pages together cover both reviews without overlap.
    ids = {first.json()["items"][0]["id"], second.json()["items"][0]["id"]}
    assert len(ids) == 2


async def test_review_permalink_includes_album(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    created = await client.put(f"/api/v1/albums/{album_id}/review", json={"rating": 4})
    review_id = created.json()["id"]

    permalink = await client.get(f"/api/v1/reviews/{review_id}")
    assert permalink.status_code == 200
    assert permalink.json()["album"]["title"] == "In Rainbows"
    assert permalink.json()["album"]["artist"]["name"] == "Radiohead"

    missing = "00000000-0000-0000-0000-000000000000"
    assert (await client.get(f"/api/v1/reviews/{missing}")).status_code == 404


async def test_user_review_listing(client: AsyncClient) -> None:
    await register(client, ALICE)
    in_rainbows = await seed_album(client, "in rainbows")
    kid_a = await seed_album(client, "kid a")
    await client.put(f"/api/v1/albums/{in_rainbows}/review", json={"rating": 5})
    await client.put(f"/api/v1/albums/{kid_a}/review", json={"rating": 4})

    listing = await client.get("/api/v1/users/alice/reviews")
    assert listing.status_code == 200
    assert listing.json()["total"] == 2
    titles = {item["album"]["title"] for item in listing.json()["items"]}
    assert titles == {"In Rainbows", "Kid A"}

    assert (await client.get("/api/v1/users/nobody/reviews")).status_code == 404


async def test_spoiler_flag_round_trips(client: AsyncClient) -> None:
    await register(client, ALICE)
    album_id = await seed_album(client)
    response = await client.put(
        f"/api/v1/albums/{album_id}/review",
        json={"rating": 4, "body": "The last track.", "contains_spoilers": True},
    )
    assert response.json()["contains_spoilers"] is True
