from app.models.models import Book
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Book]:
        query = select(Book)

        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if status:
            query = query.where(Book.status == status)

        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "release_year":
            query = query.order_by(Book.release_year)
        elif sort_by == "author":
            query = query.order_by(Book.author)

        query = query.limit(limit).offset(offset)
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

    async def delete(self, book_id: UUID) -> None:
        book = await self.get_by_id(book_id)
        if book:
            await self.db.delete(book)
            await self.db.commit()
