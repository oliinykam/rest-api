from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional

class Book(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias='_id')
    title: str
    author: str
    release_year: int
    status: str = "available"
    description: Optional[str] = None
