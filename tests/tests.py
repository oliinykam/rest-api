import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.models import books_db, Book
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    books_db.clear()
    seed_book = Book(
        title="Alice`s Adventures in Wonderland",
        author="Lewis Carroll",
        description="A novel about Alice",
        status="available",
        release_year=1865,
    )
    books_db.append(seed_book)
    yield
    books_db.clear()

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_books():
    response = client.get("/api/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Alice`s Adventures in Wonderland"

def test_get_book():
    books_response = client.get("/api/books")
    book_id = books_response.json()[0]["id"]

    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Alice`s Adventures in Wonderland"

def test_get_book_not_found():
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/books/{random_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

def test_create_book():
    new_book = {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J. K. Rowling",
        "description": "Harry",
        "status": "available",
        "release_year": 1997,
    }
    response = client.post("/api/books", json=new_book)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == new_book["title"]

def test_create_book_invalid_data():
    invalid_book = {
        "title": "Invalid Year",
        "author": "Author",
        "release_year": -1,
    }
    response = client.post("/api/books", json=invalid_book)
    assert response.status_code == 422

def test_delete_book():
    books_response = client.get("/api/books")
    book_id = books_response.json()[0]["id"]

    response = client.delete(f"/api/books/{book_id}")
    assert response.status_code == 204

    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 404