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

    async def get_by_slug_with_guides(self, db: AsyncSession, slug: str) -> Optional[DisasterType]:
        query = select(self.model).options(selectinload(self.model.guides)).filter(self.model.slug == slug)
        result = await db.execute(query)
        return result.scalars().first()

disaster_repo = DisasterRepository(DisasterType)
