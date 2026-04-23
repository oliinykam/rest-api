import uuid
import uuid6
import pytest

def test_get_books(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "Alice`s Adventures in Wonderland"

def test_get_book(client):
    books_response = client.get("/api/books")
    book_id = books_response.json()["items"][0]["id"]

    response = client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Alice`s Adventures in Wonderland"

def test_get_book_not_found(client):
    random_id = str(uuid6.uuid7())
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
    response = client.get("/api/books?limit=2")
    assert response.status_code == 200
    data = response.json()
    
    assert data["limit"] == 2
    assert "items" in data
    assert "next_cursor" in data
    assert isinstance(data["items"], list)

    if data["next_cursor"]:
        response2 = client.get(f"/api/books?limit=2&cursor={data['next_cursor']}")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["limit"] == 2
        assert "items" in data2

def test_get_books_pagination_no_duplicates(client):
    for i in range(5):
        new_book = {
            "title": f"Book {i}",
            "author": f"Author {i}",
            "description": f"Desc {i}",
            "status": "available",
            "release_year": 2000 + i,
        }
        client.post("/api/books", json=new_book)

    all_books = []
    cursor = None
    
    while True:
        url = "/api/books?limit=2"
        if cursor:
            url += f"&cursor={cursor}"
            
        res = client.get(url)
        assert res.status_code == 200
        data = res.json()
        items = data["items"]
        
        all_books.extend(items)
        
        cursor = data.get("next_cursor")
        if not cursor:
            break
            
    all_ids = [book["id"] for book in all_books]
    unique_ids = set(all_ids)
    
    assert len(all_ids) == len(unique_ids), "Found duplicate books during pagination"
    assert len(unique_ids) >= 6

def test_pagination_custom_sort_uuid_check(client):
    for i in range(3):
        new_book = {
            "title": "Identical Title",
            "author": "Identical Author",
            "description": "Desc",
            "status": "available",
            "release_year": 2020,
        }
        client.post("/api/books", json=new_book)
        
    all_books = []
    cursor = None
    
    while True:
        url = "/api/books?limit=2&sort_by=release_year"
        if cursor:
            url += f"&cursor={cursor}"
            
        res = client.get(url)
        assert res.status_code == 200
        data = res.json()
        items = data["items"]
        all_books.extend(items)
        
        cursor = data.get("next_cursor")
        if not cursor:
            break
            
    all_ids = [b["id"] for b in all_books]
    assert len(all_ids) == len(set(all_ids)), "Duplicate books found when using custom sorting"
