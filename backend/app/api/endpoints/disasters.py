from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.repositories.disaster import disaster_repo
from app.schemas.disaster import DisasterTypeResponse

router = APIRouter()

@router.get("/", response_model=List[DisasterTypeResponse])
async def get_disasters(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a list of disaster types along with their associated guides.
    """
    disasters = await disaster_repo.get_with_guides(db, skip=skip, limit=limit)
    return disasters
