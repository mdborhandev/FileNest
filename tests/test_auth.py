"""Integration tests for the auth API."""


async def register(
    client,
    email="alice@example.com",
    password="StrongPass123!",
    full_name="Alice Example",
):
    return await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )


async def login(client, email="alice@example.com", password="StrongPass123!"):
    return await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


async def refresh(client, refresh_token):
    return await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )


async def test_register_creates_user(client):
    res = await register(client)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Example"
    assert data["is_active"] is True
    assert data["last_login_at"] is None


async def test_register_rejects_duplicate_email(client):
    assert (await register(client)).status_code == 201
    res = await register(client)
    assert res.status_code == 409


async def test_register_rejects_weak_password(client):
    res = await register(client, password="password")
    assert res.status_code == 422


async def test_login_rejects_wrong_password(client):
    await register(client)
    assert (await login(client, password="WrongPass123!")).status_code == 401


async def test_login_returns_token_pair_and_me(client):
    await register(client)
    login_res = await login(client)
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"
    assert me.json()["last_login_at"] is not None


async def test_me_requires_access_token(client):
    assert (await client.get("/api/v1/auth/me")).status_code == 401


async def test_refresh_rotates_and_invalidates_previous(client):
    await register(client)
    first = (await login(client)).json()
    second = (await refresh(client, first["refresh_token"])).json()
    assert second["refresh_token"] != first["refresh_token"]

    reused = await refresh(client, first["refresh_token"])
    assert reused.status_code == 401


async def test_refresh_reuse_revokes_entire_family(client):
    await register(client)
    initial = (await login(client)).json()
    rotated = (await refresh(client, initial["refresh_token"])).json()

    assert (await refresh(client, initial["refresh_token"])).status_code == 401
    assert (await refresh(client, rotated["refresh_token"])).status_code == 401


async def test_logout_revokes_refresh_token(client):
    await register(client)
    tokens = (await login(client)).json()

    logout = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert logout.status_code == 204
    assert (await refresh(client, tokens["refresh_token"])).status_code == 401
