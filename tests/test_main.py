from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_book():
    response = client.post(
        "/books/",
        json={
            "title": "1984",
            "author": "George Orwell",
            "publication_year": 1949,
            "genre": "Fiction"
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "1984"
