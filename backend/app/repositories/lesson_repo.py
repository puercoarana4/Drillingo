import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson


class LessonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_dialect_and_level(
        self,
        dialect: Optional[str] = None,
        level: Optional[str] = None,
    ) -> list[Lesson]:
        """
        Return lessons filtered by dialect_segment and/or level_band.
        If neither is provided, returns all lessons ordered by day_order (Req 3.5).
        """
        query = select(Lesson)
        if dialect:
            query = query.where(Lesson.dialect_segment == dialect)
        if level:
            query = query.where(Lesson.level_band == level)
        query = query.order_by(Lesson.day_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def find_all_ordered_by_day(self) -> list[Lesson]:
        """Return all lessons ordered by day_order regardless of dialect or level."""
        result = await self.db.execute(select(Lesson).order_by(Lesson.day_order))
        return list(result.scalars().all())

    async def get_by_id(self, lesson_id: uuid.UUID | str) -> Optional[Lesson]:
        """Return a single lesson by primary key, or None if not found."""
        result = await self.db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        return result.scalar_one_or_none()
