from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.repositories.base import BaseRepository
from app.models.disaster import DisasterType

class DisasterRepository(BaseRepository[DisasterType]):
    async def get_with_guides(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[DisasterType]:
        query = select(self.model).options(selectinload(self.model.guides)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

disaster_repo = DisasterRepository(DisasterType)
