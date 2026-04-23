import uuid
import uuid6
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from app.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid6.uuid7, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="available")
    description = Column(Text, nullable=True)