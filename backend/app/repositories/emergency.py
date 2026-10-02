from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.repositories.base import BaseRepository
from app.models.emergency import EmergencyNumber, Department

class EmergencyNumberRepository(BaseRepository[EmergencyNumber]):
    async def get_by_category(self, db: AsyncSession, category: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[EmergencyNumber]:
        query = select(self.model)
        if category:
            query = query.filter(self.model.category == category)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

class DepartmentRepository(BaseRepository[Department]):
    async def get_by_category(self, db: AsyncSession, category: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Department]:
        query = select(self.model)
        if category:
            query = query.filter(self.model.category == category)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

emergency_number_repo = EmergencyNumberRepository(EmergencyNumber)
department_repo = DepartmentRepository(Department)
