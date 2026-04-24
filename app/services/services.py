from app.repository.repository import BookRepository
from app.models.models import Book
from app.schemas.schemas import BookRequest, BookStatus, SortOrder
from pydantic_mongo import PydanticObjectId
from typing import List, Optional, Tuple
from pymongo.database import Database


class BookService:
    def __init__(self, db: Database):
        self.repo = BookRepository(db)

    def get_books(
        self,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
        sort_by: Optional[str] = None,
        order: SortOrder = SortOrder.ASC,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[Book], int]:
        status_val = status.value if status else None
        items = self.repo.get_all(
            author=author,
            status=status_val,
            sort_by=sort_by,
            order=order.value if order else "asc",
            limit=limit,
            offset=offset
        )
        total = self.repo.count(author=author, status=status_val)
        return items, total

    def get_book(self, book_id: PydanticObjectId) -> Optional[Book]:
        return self.repo.get_by_id(book_id)

    def create_book(self, book_in: BookRequest) -> Book:
        new_book = Book(
            title=book_in.title,
            author=book_in.author,
            release_year=book_in.release_year,
            status=book_in.status.value,
            description=book_in.description
        )
        return self.repo.add(new_book)

    def delete_book(self, book_id: PydanticObjectId) -> bool:
        return self.repo.delete(book_id)
