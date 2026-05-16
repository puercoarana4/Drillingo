import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import VocabularyItem


class VocabularyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_dialect_and_level(
        self,
        dialect: Optional[str] = None,
        level: Optional[str] = None,
    ) -> list[VocabularyItem]:
        """
        Return vocabulary items filtered by dialect_segment and/or level_band.
        If neither is provided, returns all items (Req 3.3).
        """
        query = select(VocabularyItem)
        if dialect:
            query = query.where(VocabularyItem.dialect_segment == dialect)
        if level:
            query = query.where(VocabularyItem.level_band == level)
        query = query.order_by(VocabularyItem.term)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, item_id: uuid.UUID | str) -> Optional[VocabularyItem]:
        """Return a single vocabulary item by primary key, or None if not found."""
        result = await self.db.execute(
            select(VocabularyItem).where(VocabularyItem.id == item_id)
        )
        return result.scalar_one_or_none()
