from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewsItemBase(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    summary: Optional[str] = None
    disaster_slug: Optional[str] = None
    city: Optional[str] = None
    published_at: Optional[datetime] = None

class NewsItemResponse(NewsItemBase):
    id: str
    fetched_at: datetime

    class Config:
        from_attributes = True
