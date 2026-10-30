from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.db.database import get_db
from app.models.alert import NewsItem
from app.schemas.news import NewsItemResponse

router = APIRouter()

@router.get("/", response_model=List[NewsItemResponse])
async def get_news(
    city: Optional[str] = Query(None, description="Filter by city name"),
    disaster: Optional[str] = Query(None, description="Filter by disaster slug"),
    limit: int = Query(20, ge=1, le=50, description="Limit results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get nearby incident news.
    """
    stmt = select(NewsItem)
    
    if city:
        stmt = stmt.where(NewsItem.city.ilike(f"%{city}%"))
    if disaster:
        stmt = stmt.where(NewsItem.disaster_slug == disaster)
        
    # Sort by published_at DESC
    stmt = stmt.order_by(desc(NewsItem.published_at))
    stmt = stmt.limit(limit)
    
    result = await db.execute(stmt)
    news = result.scalars().all()
    
    return news
