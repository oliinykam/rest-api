import pytest
import uuid

@pytest.mark.asyncio
async def test_get_books(async_client):
    response = await async_client.get("/api/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "Alice`s Adventures in Wonderland"

@pytest.mark.asyncio
async def test_get_book(async_client):
    books_response = await async_client.get("/api/books")
    book_id = books_response.json()["items"][0]["id"]

    response = await async_client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Alice`s Adventures in Wonderland"

@pytest.mark.asyncio
async def test_get_book_not_found(async_client):
    random_id = str(uuid.uuid4())
    response = await async_client.get(f"/api/books/{random_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

@pytest.mark.asyncio
async def test_create_book(async_client):
    new_book = {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J. K. Rowling",
        "description": "Harry",
        "status": "available",
        "release_year": 1997,
    }
    response = await async_client.post("/api/books", json=new_book)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == new_book["title"]

@pytest.mark.asyncio
async def test_create_book_invalid_data(async_client):
    invalid_book = {
        "title": "Invalid Year",
        "author": "Author",
        "release_year": -1,
    }
    response = await async_client.post("/api/books", json=invalid_book)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_book(async_client):
    books_response = await async_client.get("/api/books")
    book_id = books_response.json()["items"][0]["id"]

    response = await async_client.delete(f"/api/books/{book_id}")
    assert response.status_code == 204

    response = await async_client.get(f"/api/books/{book_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_books_pagination(async_client):
    response = await async_client.get("/api/books?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
