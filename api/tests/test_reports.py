from datetime import date

# Тесты для /monthly/


def test_monthly_report_empty_db(client):
    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()
    assert data["total_cents"] == 0


def test_monthly_report_with_expenses(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2026, 8, 15))
    create_expense_fixture(category, 30000, date(2026, 8, 20))

    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()
    assert data["total_cents"] == 80000


def test_monthly_report_first_day_of_month(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2026, 8, 1))

    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    assert response.json()["total_cents"] == 50000


def test_monthly_report_last_day_of_month(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2026, 8, 31))

    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    assert response.json()["total_cents"] == 50000


def test_monthly_report_excludes_other_months(
    client, create_category_fixture, create_expense_fixture
):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2026, 7, 31))
    create_expense_fixture(category, 30000, date(2026, 8, 15))
    create_expense_fixture(category, 20000, date(2026, 9, 1))

    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    assert response.json()["total_cents"] == 30000


def test_monthly_report_february_leap_year(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2024, 2, 29))

    response = client.get("/api/v1/reports/monthly/", params={"year": 2024, "month": 2})

    assert response.status_code == 200
    assert response.json()["total_cents"] == 50000


def test_monthly_report_invalid_month(client):
    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 13})

    assert response.status_code == 422


def test_monthly_report_invalid_month_zero(client):
    response = client.get("/api/v1/reports/monthly/", params={"year": 2026, "month": 0})

    assert response.status_code == 422


# Тесты для /by-categories/


def test_by_categories_empty_db(client):
    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()
    assert data["categories"] == []


def test_by_categories_with_expenses(client, create_category_fixture, create_expense_fixture):
    food = create_category_fixture("Еда")
    transport = create_category_fixture("Транспорт")

    create_expense_fixture(food, 50000, date(2026, 8, 15))
    create_expense_fixture(transport, 30000, date(2026, 8, 20))

    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()
    assert len(data["categories"]) == 2

    assert data["categories"][0]["name"] == "Еда"
    assert data["categories"][0]["total_cents"] == 50000

    assert data["categories"][1]["name"] == "Транспорт"
    assert data["categories"][1]["total_cents"] == 30000


def test_by_categories_category_without_expenses(
    client, create_category_fixture, create_expense_fixture
):
    food = create_category_fixture("Еда")
    create_category_fixture("Подарки")

    create_expense_fixture(food, 50000, date(2026, 8, 15))

    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()
    assert len(data["categories"]) == 2

    category_names = [c["name"] for c in data["categories"]]
    assert "Подарки" in category_names

    gifts_category = next(c for c in data["categories"] if c["name"] == "Подарки")
    assert gifts_category["total_cents"] == 0


def test_by_categories_sorted_by_total_desc(
    client, create_category_fixture, create_expense_fixture
):
    food = create_category_fixture("Еда")
    transport = create_category_fixture("Транспорт")

    create_expense_fixture(food, 30000, date(2026, 8, 15))
    create_expense_fixture(transport, 50000, date(2026, 8, 20))

    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()

    assert data["categories"][0]["name"] == "Транспорт"
    assert data["categories"][1]["name"] == "Еда"


def test_by_categories_excludes_other_months(
    client, create_category_fixture, create_expense_fixture
):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2026, 7, 15))
    create_expense_fixture(category, 30000, date(2026, 8, 15))

    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    data = response.json()
    assert data["categories"][0]["total_cents"] == 30000


def test_by_categories_boundary_dates(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    create_expense_fixture(category, 10000, date(2026, 8, 1))
    create_expense_fixture(category, 20000, date(2026, 8, 31))

    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 8})

    assert response.status_code == 200
    assert response.json()["categories"][0]["total_cents"] == 30000


def test_by_categories_february_leap_year(client, create_category_fixture, create_expense_fixture):
    category = create_category_fixture()
    create_expense_fixture(category, 50000, date(2024, 2, 29))

    response = client.get("/api/v1/reports/by-categories/", params={"year": 2024, "month": 2})

    assert response.status_code == 200
    assert response.json()["categories"][0]["total_cents"] == 50000


def test_by_categories_invalid_month(client):
    response = client.get("/api/v1/reports/by-categories/", params={"year": 2026, "month": 13})

    assert response.status_code == 422
