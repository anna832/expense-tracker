def test_register(client):
    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "testpass123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data


def test_register_duplicate_username(client):
    client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "testpass123"},
    )

    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "otherpass"},
    )

    assert response.status_code == 400


def test_login_success(client):
    client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "testpass123"},
    )

    response = client.post(
        "/api/v1/auth/login/",
        json={"username": "testuser", "password": "testpass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "testpass123"},
    )

    response = client.post(
        "/api/v1/auth/login/",
        json={"username": "testuser", "password": "wrongpass"},
    )

    assert response.status_code == 401


def test_me_endpoint(client, auth_headers):
    headers, user = auth_headers()

    response = client.get("/api/v1/auth/me/", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == user.username


def test_access_without_token(client):
    response = client.get("/api/v1/expenses/")
    assert response.status_code == 401


def test_access_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/api/v1/expenses/", headers=headers)
    assert response.status_code == 401


def test_register_short_username(client):
    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "ab", "password": "testpass123"},
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "short"},
    )

    assert response.status_code == 422


def test_login_short_password_returns_401(client):
    response = client.post(
        "/api/v1/auth/login/",
        json={
            "username": "maria",
            "password": "123",
        },
    )
    assert response.status_code == 401


def test_register_password_too_long_returns_422(client):
    long_password = "a" * 129
    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": long_password},
    )
    assert response.status_code == 422


def test_register_password_exactly_128_chars_ok(client):
    boundary_password = "a" * 128
    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": boundary_password},
    )
    assert response.status_code == 201


def test_register_password_exactly_8_chars_ok(client):
    response = client.post(
        "/api/v1/auth/register/",
        json={"username": "testuser", "password": "validpass"},
    )
    assert response.status_code == 201


def test_register_long_comment_in_expense(client, auth_headers, create_category_fixture):
    headers, _ = auth_headers()
    category = create_category_fixture("Еда")

    long_comment = "x" * 300

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-15",
            "comment": long_comment,
        },
        headers=headers,
    )

    assert response.status_code == 422
