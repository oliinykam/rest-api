"""Tests for authentication endpoints: register, login, refresh (token rotation), logout."""


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client):
    payload = {"username": "duplicate", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_register_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "user1", "password": "abc"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"username": "loginuser", "password": "securepass"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser", "password": "securepass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"username": "loginuser2", "password": "securepass"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser2", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "ghost", "password": "password123"},
    )
    assert response.status_code == 401


def test_refresh_token_success(client):
    """Refresh token returns new access + refresh tokens."""
    client.post(
        "/api/auth/register",
        json={"username": "refreshuser", "password": "password123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "refreshuser", "password": "password123"},
    )
    old_refresh = login_resp.json()["refresh_token"]
    old_access = login_resp.json()["access_token"]

    refresh_resp = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != old_access
    assert data["refresh_token"] != old_refresh


def test_refresh_token_rotation_invalidates_old_token(client):
    """After rotation, the old refresh token must be rejected (used only once)."""
    client.post(
        "/api/auth/register",
        json={"username": "rotateuser", "password": "password123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "rotateuser", "password": "password123"},
    )
    old_refresh = login_resp.json()["refresh_token"]

    client.post("/api/auth/refresh", json={"refresh_token": old_refresh})

    second_resp = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert second_resp.status_code == 401


def test_refresh_with_invalid_token(client):
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": "not.a.valid.token"}
    )
    assert response.status_code == 401


def test_logout_success(client):
    client.post(
        "/api/auth/register",
        json={"username": "logoutuser", "password": "password123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "logoutuser", "password": "password123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = client.post("/api/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    refresh_resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 401
