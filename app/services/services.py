from app.repository.repository import BookRepository
from app.models.models import Book
from app.schemas.schemas import BookRequest, BookStatus, SortOrder
from uuid import UUID
from typing import List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
import base64
import json


class BookService:
    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    def _encode_cursor(self, book: Book, sort_by: Optional[str]) -> str:
        sort_by_val = sort_by.value if hasattr(sort_by, 'value') else sort_by
        sort_val = getattr(book, sort_by_val) if sort_by_val else None
        if sort_val is not None:
            sort_val = str(sort_val)
        data = {"sort_val": sort_val, "id": str(book.id)}
        return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

    def _decode_cursor(self, cursor: str, sort_by: Optional[str]) -> Tuple[Any, Optional[UUID]]:
        try:
            decoded = base64.b64decode(cursor).decode('utf-8')
            data = json.loads(decoded)
            sort_val = data.get('sort_val')
            sort_by_val = sort_by.value if hasattr(sort_by, 'value') else sort_by
            if sort_val is not None and sort_by_val == 'release_year':
                sort_val = int(sort_val)
            return sort_val, UUID(data['id'])
        except Exception:
            return None, None

    async def get_books(
        self,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
        sort_by: Optional[str] = None,
        order: SortOrder = SortOrder.ASC,
        limit: int = 10,
        cursor: Optional[str] = None
    ) -> Tuple[List[Book], Optional[str]]:
        status_val = status.value if status else None
        sort_by_val = sort_by.value if hasattr(sort_by, 'value') else sort_by

        cursor_sort_val, cursor_id = None, None
        if cursor:
            cursor_sort_val, cursor_id = self._decode_cursor(cursor, sort_by)

        items = await self.repo.get_all(
            author=author,
            status=status_val,
            sort_by=sort_by_val,
            order=order.value,
            limit=limit + 1,
            cursor_sort_val=cursor_sort_val,
            cursor_id=cursor_id
        )

        next_cursor = None
        if len(items) > limit:
            items = items[:limit]
            last_item = items[-1]
            next_cursor = self._encode_cursor(last_item, sort_by)

        return items, next_cursor

    async def get_book(self, book_id: UUID) -> Optional[Book]:
        return await self.repo.get_by_id(book_id)

    async def create_book(self, book_in: BookRequest) -> Book:
        new_book = Book(
            title=book_in.title,
            author=book_in.author,
            release_year=book_in.release_year,
            status=book_in.status.value,
            description=book_in.description
        )
        return await self.repo.add(new_book)

    async def delete_book(self, book_id: UUID) -> bool:
        return await self.repo.delete(book_id)
