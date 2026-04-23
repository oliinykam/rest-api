import uuid
import pytest

def test_get_books(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "Alice's Adventures in Wonderland"

def test_get_book(client):
    books_response = client.get("/api/books")
    book_id = books_response.json()["items"][0]["id"]

    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Alice's Adventures in Wonderland"

from bson import ObjectId

def test_get_book_not_found(client):
    random_id = str(ObjectId())
    response = client.get(f"/api/books/{random_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

def test_create_book(client):
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

def test_create_book_invalid_data(client):
    invalid_book = {
        "title": "Invalid Year",
        "author": "Author",
        "release_year": -1,
    }
    response = client.post("/api/books", json=invalid_book)
    assert response.status_code == 422

def test_delete_book(client):
    books_response = client.get("/api/books")
    book_id = books_response.json()["items"][0]["id"]

    response = client.delete(f"/api/books/{book_id}")
    assert response.status_code == 204

    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 404

def test_get_books_pagination(client):
    response = client.get("/api/books?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
