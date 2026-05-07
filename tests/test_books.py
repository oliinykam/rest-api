import uuid


def test_get_books(client, auth_headers):
    response = client.get("/api/books", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "Alice`s Adventures in Wonderland"


def test_get_book(client, auth_headers):
    books_response = client.get("/api/books", headers=auth_headers)
    book_id = books_response.json()["items"][0]["id"]

    response = client.get(f"/api/books/{book_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Alice`s Adventures in Wonderland"


def test_get_book_not_found(client, auth_headers):
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/books/{random_id}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_create_book(client, auth_headers):
    new_book = {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J. K. Rowling",
        "description": "Harry",
        "status": "available",
        "release_year": 1997,
    }
    response = client.post("/api/books", json=new_book, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == new_book["title"]


def test_create_book_invalid_data(client, auth_headers):
    invalid_book = {
        "title": "Invalid Year",
        "author": "Author",
        "release_year": -1,
    }
    response = client.post("/api/books", json=invalid_book, headers=auth_headers)
    assert response.status_code == 422


def test_delete_book(client, auth_headers):
    books_response = client.get("/api/books", headers=auth_headers)
    book_id = books_response.json()["items"][0]["id"]

    response = client.delete(f"/api/books/{book_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/api/books/{book_id}", headers=auth_headers)
    assert response.status_code == 404


def test_get_books_pagination(client, auth_headers):
    response = client.get("/api/books?limit=2&offset=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["limit"] == 2
    assert data["offset"] == 0
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_books_require_auth(client):
    """All /books endpoints must return 401 without a valid token."""
    assert client.get("/api/books").status_code == 401
    assert client.post("/api/books", json={}).status_code == 401
