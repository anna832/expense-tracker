from datetime import date


def test_create_expense(client, auth_headers, create_category_fixture):
    headers, _ = auth_headers()
    category = create_category_fixture("Еда")

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-15",
            "comment": "Обед",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] == category.id
    assert data["amount_cents"] == 50000
    assert data["comment"] == "Обед"


def test_create_expense_with_invalid_category(client, auth_headers):
    headers, _ = auth_headers()

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": 999,
            "amount_cents": 50000,
            "spent_at": "2026-08-15",
            "comment": "Обед",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Category not found"


def test_create_expense_with_negative_amount(client, auth_headers, create_category_fixture):
    headers, _ = auth_headers()
    category = create_category_fixture("Еда")

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": -100,
            "spent_at": "2026-08-15",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_create_expense_without_token(client, create_category_fixture):
    category = create_category_fixture("Еда")

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-15",
        },
    )

    assert response.status_code == 401


def test_list_expenses(client, auth_headers, create_category_fixture, create_expense_fixture):
    headers, user = auth_headers()
    category = create_category_fixture()

    for i in range(3):
        create_expense_fixture(
            category,
            1000 * (i + 1),
            date(2026, 8, 10 + i),
            f"Трата {i + 1}",
            user_id=user.id,
        )

    response = client.get("/api/v1/expenses/", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert data["skip"] == 0
    assert data["limit"] == 50
    assert len(data["items"]) == 3


def test_list_expenses_without_token(client):
    response = client.get("/api/v1/expenses/")
    assert response.status_code == 401


def test_get_expense_by_id(client, auth_headers, create_category_fixture, create_expense_fixture):
    headers, user = auth_headers()
    category = create_category_fixture()
    expense = create_expense_fixture(category, 50000, date(2026, 8, 15), "Обед", user_id=user.id)

    response = client.get(f"/api/v1/expenses/{expense.id}/", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == expense.id
    assert data["amount_cents"] == 50000
    assert data["comment"] == "Обед"


def test_get_expense_not_found(client, auth_headers):
    headers, _ = auth_headers()

    response = client.get("/api/v1/expenses/999/", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


def test_update_expense(client, auth_headers, create_category_fixture, create_expense_fixture):
    headers, user = auth_headers()
    category = create_category_fixture()
    expense = create_expense_fixture(category, 50000, date(2026, 8, 15), "Обед", user_id=user.id)

    response = client.patch(
        f"/api/v1/expenses/{expense.id}/",
        json={"amount_cents": 75000, "comment": "Ужин"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["amount_cents"] == 75000
    assert data["comment"] == "Ужин"


def test_delete_expense(client, auth_headers, create_category_fixture, create_expense_fixture):
    headers, user = auth_headers()
    category = create_category_fixture()
    expense = create_expense_fixture(category, 50000, date(2026, 8, 15), user_id=user.id)

    response = client.delete(f"/api/v1/expenses/{expense.id}/", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/expenses/{expense.id}/", headers=headers)
    assert response.status_code == 404
