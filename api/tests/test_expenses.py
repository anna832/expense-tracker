from app.models import Category


def create_category(db_session, name="Еда"):
    category = Category(name=name)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def test_create_expense(client, db_session):
    category = create_category(db_session)

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] == category.id
    assert data["amount_cents"] == 50000
    assert data["comment"] == "Такси"


def test_create_expense_with_invalid_category(client):
    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": 999,
            "amount_cents": 50000,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )

    assert response.status_code == 400


def test_create_expense_with_negative_amount(client, db_session):
    category = create_category(db_session)

    response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": -100,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )

    assert response.status_code == 422


def test_list_expenses(client, db_session):
    category = create_category(db_session)

    client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )

    response = client.get("/api/v1/expenses/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_expense_by_id(client, db_session):
    category = create_category(db_session)

    create_response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )
    expense_id = create_response.json()["id"]

    response = client.get(f"/api/v1/expenses/{expense_id}/")

    assert response.status_code == 200
    assert response.json()["id"] == expense_id


def test_get_expense_not_found(client):
    response = client.get("/api/v1/expenses/999/")

    assert response.status_code == 404


def test_update_expense(client, db_session):
    category = create_category(db_session)

    create_response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )
    expense_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/expenses/{expense_id}/",
        json={
            "amount_cents": 70000,
        },
    )

    assert response.status_code == 200
    assert response.json()["amount_cents"] == 70000


def test_delete_expense(client, db_session):
    category = create_category(db_session)

    create_response = client.post(
        "/api/v1/expenses/",
        json={
            "category_id": category.id,
            "amount_cents": 50000,
            "spent_at": "2026-08-12",
            "comment": "Такси",
        },
    )
    expense_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/expenses/{expense_id}/")

    assert response.status_code == 204

    get_response = client.get(f"/api/v1/expenses/{expense_id}/")
    assert get_response.status_code == 404