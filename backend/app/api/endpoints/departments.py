from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.repositories.emergency import department_repo
from app.schemas.emergency import DepartmentResponse

router = APIRouter()

@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a list of departments, optionally filtered by category.
    """
    departments = await department_repo.get_by_category(db, category=category, skip=skip, limit=limit)
    return departments
