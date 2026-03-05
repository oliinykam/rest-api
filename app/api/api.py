from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.schemas import BookRequest, BookResponse, BookStatus
from app.services.services import BookService
from uuid import UUID
from typing import List, Optional

router = APIRouter(prefix="/api", tags=["Books"])
service = BookService()

@router.get("/health")
async def check_health():
    return {"status": "ok"}

@router.get("/books", response_model=List[BookResponse])
async def get_all_books(sort_by: Optional[str] = None):
    return await service.get_books(sort_by=sort_by)

@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: UUID):
    book = await service.get_book(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    return await service.create_book(book)

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    return await service.delete_book(book_id)