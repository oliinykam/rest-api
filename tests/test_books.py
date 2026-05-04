import pytest
from bson import ObjectId

def test_get_books(client_app):
    response = client_app.get("/api/books")
    assert response.status_code == 200
    data = response.get_json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "Alice's Adventures in Wonderland"

def test_get_book(client_app):
    books_response = client_app.get("/api/books")
    book_id = books_response.get_json()["items"][0]["id"]

    response = client_app.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Alice's Adventures in Wonderland"

def test_get_book_not_found(client_app):
    random_id = str(ObjectId())
    response = client_app.get(f"/api/books/{random_id}")
    assert response.status_code == 404
    assert response.get_json()["detail"] == "Book not found"

def test_create_book(client_app):
    new_book = {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J. K. Rowling",
        "description": "Harry",
        "status": "available",
        "release_year": 1997,
    }
    response = client_app.post("/api/books", json=new_book)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["title"] == new_book["title"]

def test_create_book_invalid_data(client_app):
    invalid_book = {
        "title": "Invalid Year",
        "author": "Author",
        "release_year": -1,
    }
    response = client_app.post("/api/books", json=invalid_book)
    assert response.status_code == 422

def test_delete_book(client_app):
    books_response = client_app.get("/api/books")
    book_id = books_response.get_json()["items"][0]["id"]

    response = client_app.delete(f"/api/books/{book_id}")
    assert response.status_code == 204

    response = client_app.get(f"/api/books/{book_id}")
    assert response.status_code == 404

def test_get_books_pagination(client_app):
    response = client_app.get("/api/books?limit=2&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)