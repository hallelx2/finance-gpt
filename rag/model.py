from pydantic import BaseModel, HttpUrl
from typing import Optional

# Define the Model Sxhema to store the documents in MongoD
class DocumentModel(BaseModel):
    category: str
    datetime: int
    headline: str
    id: int
    image: Optional[str] = None
    related: str
    source: str
    summary: str
    url: str
    ticker: str
    date: str

    class Config:
        from_attributes = True
