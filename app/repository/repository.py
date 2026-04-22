from app.models.models import Book
from uuid import UUID
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc, func

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _build_query(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        cursor_sort_val: Optional[str] = None,
        cursor_id: Optional[UUID] = None,
    ):
        query = select(Book)

        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if status:
            query = query.where(Book.status == status)

        is_desc = order.lower() == "desc"
        sort_func = desc if is_desc else asc

        if cursor_id:
            if sort_by:
                sort_col = getattr(Book, sort_by)
                if is_desc:
                    query = query.where(
                        (sort_col < cursor_sort_val) |
                        ((sort_col == cursor_sort_val) & (Book.id < cursor_id))
                    )
                else:
                    query = query.where(
                        (sort_col > cursor_sort_val) |
                        ((sort_col == cursor_sort_val) & (Book.id > cursor_id))
                    )
            else:
                if is_desc:
                    query = query.where(Book.id < cursor_id)
                else:
                    query = query.where(Book.id > cursor_id)

        if sort_by:
            sort_col = getattr(Book, sort_by)
            query = query.order_by(sort_func(sort_col), sort_func(Book.id))
        else:
            query = query.order_by(sort_func(Book.id))

        return query

    async def count(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        query = select(func.count()).select_from(Book)
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if status:
            query = query.where(Book.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_all(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        limit: int = 10,
        cursor_sort_val: Optional[str] = None,
        cursor_id: Optional[UUID] = None,
    ) -> List[Book]:
        query = self._build_query(
            author=author,
            status=status,
            sort_by=sort_by,
            order=order,
            cursor_sort_val=cursor_sort_val,
            cursor_id=cursor_id
        )
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        result = await self.db.execute(select(Book).where(Book.id == book_id))
        return result.scalars().first()

    async def add(self, book: Book) -> Book:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete(self, book_id: UUID) -> bool:
        book = await self.get_by_id(book_id)
        if book:
            await self.db.delete(book)
            await self.db.commit()
            return True
        return False
