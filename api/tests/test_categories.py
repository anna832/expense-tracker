from app.models import Category


def test_list_categories_empty(client):
    response = client.get("/api/v1/categories/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_categories_with_data(client, db_session):
    category = Category(name="Еда")
    db_session.add(category)
    db_session.commit()

    response = client.get("/api/v1/categories/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Еда"
