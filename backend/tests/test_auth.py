from httpx import AsyncClient

REGISTER = {"email": "alice@noted.dev", "username": "Alice", "password": "correct-horse-battery"}


async def test_register_sets_cookies_and_returns_user(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json=REGISTER)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["username"] == "alice"  # normalised to lowercase
    assert body["email"] == "alice@noted.dev"
    assert "password_hash" not in body
    assert "noted_access" in response.cookies
    assert "noted_refresh" in response.cookies


async def test_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_register_then_me_then_logout(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER)

    me = await client.get("/api/v1/users/me")
    assert me.status_code == 200
    assert me.json()["username"] == "alice"

    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    me_again = await client.get("/api/v1/users/me")
    assert me_again.status_code == 401


async def test_duplicate_username_is_rejected(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER)
    dup = await client.post("/api/v1/auth/register", json={**REGISTER, "email": "other@noted.dev"})
    assert dup.status_code == 409
    assert "username" in dup.json()["detail"]


async def test_login_with_email_or_username(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER)
    await client.post("/api/v1/auth/logout")

    by_email = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "ALICE@noted.dev", "password": REGISTER["password"]},
    )
    assert by_email.status_code == 200

    by_username = await client.post(
        "/api/v1/auth/login", json={"identifier": "alice", "password": REGISTER["password"]}
    )
    assert by_username.status_code == 200


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER)
    bad = await client.post("/api/v1/auth/login", json={"identifier": "alice", "password": "nope"})
    assert bad.status_code == 401


async def test_refresh_issues_new_access_cookie(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER)
    client.cookies.delete("noted_access")
    assert (await client.get("/api/v1/users/me")).status_code == 401

    refreshed = await client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200
    assert "noted_access" in refreshed.cookies
    assert (await client.get("/api/v1/users/me")).status_code == 200


async def test_public_profile(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER)
    profile = await client.get("/api/v1/users/alice")
    assert profile.status_code == 200
    assert "email" not in profile.json()
    assert (await client.get("/api/v1/users/nobody")).status_code == 404
