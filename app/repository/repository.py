from app.models.models import Book, books_db
from uuid import UUID
from typing import List, Optional

class BookRepository:
    async def get_all(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[Book]:
        result = list(books_db)

        if author:
            result = [b for b in result if author.lower() in b.author.lower()]
        if status:
            result = [b for b in result if b.status == status]

        if sort_by == "title":
            result.sort(key=lambda x: x.title)
        elif sort_by == "release_year":
            result.sort(key=lambda x: x.release_year)

        return result

    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        return next((b for b in books_db if b.id == book_id), None)

    async def add(self, book: Book) -> Book:
        books_db.append(book)
        return book

    async def delete(self, book_id: UUID) -> None:
        global books_db
        books_db[:] = [b for b in books_db if b.id != book_id]