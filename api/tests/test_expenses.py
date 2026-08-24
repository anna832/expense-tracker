from datetime import date


def test_create_expense(client, create_category_fixture):
    category = create_category_fixture("Еда")

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-15",
            "comment": "Обед",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] == category.id
    assert data["amount_cents"] == 50000
    assert data["comment"] == "Обед"


def test_create_expense_with_invalid_category(client):
    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": 999,
            "amount_cents": 50000,
            "spent_at": "2026-08-15",
            "comment": "Обед",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Category not found"


def test_create_expense_with_negative_amount(client, create_category_fixture):
    category = create_category_fixture("Еда")

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": -100,
            "spent_at": "2026-08-15",
        },
    )

    assert response.status_code == 422


def test_list_expenses(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()

    for i in range(3):
        create_expense_fixture(
            category,
            1000 * (i + 1),
            date(2026, 8, 10 + i),
            f"Трата {i + 1}",
        )

    response = client.get("/api/v1/expenses/")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert data["skip"] == 0
    assert data["limit"] == 50
    assert len(data["items"]) == 3


def test_list_expenses_with_pagination(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()

    for i in range(10):
        create_expense_fixture(category, 1000, date(2026, 8, 10 + i))

    response = client.get("/api/v1/expenses/?skip=0&limit=3")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 10
    assert data["limit"] == 3
    assert len(data["items"]) == 3

    response = client.get("/api/v1/expenses/?skip=3&limit=3")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 10
    assert data["skip"] == 3
    assert len(data["items"]) == 3


def test_list_expenses_filter_by_category(client, create_category_fixture, create_expense_fixture):
    food = create_category_fixture("Еда")
    transport = create_category_fixture("Транспорт")

    create_expense_fixture(food, 1000, date(2026, 8, 15))
    create_expense_fixture(transport, 2000, date(2026, 8, 15))

    response = client.get(f"/api/v1/expenses/?category_id={food.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category_id"] == food.id


def test_list_expenses_filter_by_date_range(
    client, create_category_fixture, create_expense_fixture
):
    category = create_category_fixture()

    create_expense_fixture(category, 1000, date(2026, 8, 5))
    create_expense_fixture(category, 2000, date(2026, 8, 15))
    create_expense_fixture(category, 3000, date(2026, 8, 25))

    response = client.get("/api/v1/expenses/?date_from=2026-08-10&date_to=2026-08-20")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["amount_cents"] == 2000


def test_list_expenses_limit_validation(client):
    response = client.get("/api/v1/expenses/?limit=200")
    assert response.status_code == 422

    response = client.get("/api/v1/expenses/?skip=-1")
    assert response.status_code == 422


def test_get_expense_by_id(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    expense = create_expense_fixture(category, 50000, date(2026, 8, 15), "Обед")

    response = client.get(f"/api/v1/expenses/{expense.id}/")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == expense.id
    assert data["amount_cents"] == 50000
    assert data["comment"] == "Обед"


def test_get_expense_not_found(client):
    response = client.get("/api/v1/expenses/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


def test_update_expense(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    expense = create_expense_fixture(category, 50000, date(2026, 8, 15), "Обед")

    response = client.patch(
        f"/api/v1/expenses/{expense.id}/",
        json={"amount_cents": 75000, "comment": "Ужин"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["amount_cents"] == 75000
    assert data["comment"] == "Ужин"


def test_delete_expense(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    expense = create_expense_fixture(category, 50000, date(2026, 8, 15))

    response = client.delete(f"/api/v1/expenses/{expense.id}/")
    assert response.status_code == 204

    response = client.get(f"/api/v1/expenses/{expense.id}/")
    assert response.status_code == 404
