from app.models.models import Book
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import re

class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.books

    def _build_query(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        query = {}
        if author:
            query["author"] = {"$regex": author, "$options": "i"}
        if status:
            query["status"] = status
        return query

    async def count(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        query = self._build_query(author, status)
        return await self.collection.count_documents(query)

    async def get_all(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ) -> List[Book]:
        query = self._build_query(author, status)
        cursor = self.collection.find(query)
        
        if sort_by:
            sort_dir = 1 if order.lower() == "asc" else -1
            if sort_by == "id":
                sort_by = "_id"
            cursor = cursor.sort(sort_by, sort_dir)
            
        cursor = cursor.skip(offset).limit(limit)
        items = await cursor.to_list(length=limit)
        return [Book(**item) for item in items]

    async def get_by_id(self, book_id: PydanticObjectId) -> Optional[Book]:
        item = await self.collection.find_one({"_id": PydanticObjectId(book_id)})
        if item:
            return Book(**item)
        return None

    async def add(self, book: Book) -> Book:
        book_dict = book.model_dump(by_alias=True, exclude_none=True)
        await self.collection.insert_one(book_dict)
        return book

    async def delete(self, book_id: PydanticObjectId) -> None:
        await self.collection.delete_one({"_id": PydanticObjectId(book_id)})
