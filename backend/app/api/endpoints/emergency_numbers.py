from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.repositories.emergency import emergency_number_repo
from app.schemas.emergency import EmergencyNumberResponse

router = APIRouter()

@router.get("/", response_model=List[EmergencyNumberResponse])
async def get_emergency_numbers(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a list of emergency numbers, optionally filtered by category.
    """
    numbers = await emergency_number_repo.get_by_category(db, category=category, skip=skip, limit=limit)
    return numbers
