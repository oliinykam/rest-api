from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional, List

@dataclass
class Book:
    title: str
    author: str
    release_year: int
    status: str
    description: Optional[str] = None
    id: UUID = field(default_factory=uuid4)

books_db: List[Book] = [
    Book(
            title="The Little Prince",
            author="Antoine de Saint-Exupéry",
            description="A novel about little prince",
            status="available",
            release_year=1943,
        ),
    Book(
            title="The Alchemist",
            author="Paulo Coelho",
            description="A novel about jorney boy",
            status="available",
            release_year=1988,
        ),
    Book(
            title="The Da Vinci Code",
            author="Dan Brown",
            description="A mystery thriller novel",
            status="issued",
            release_year=2003,
        )
]