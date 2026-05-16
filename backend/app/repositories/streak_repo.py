import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.streak import Streak


class StreakRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Streak]:
        """Return the streak record for a user, or None if it doesn't exist yet."""
        result = await self.db.execute(
            select(Streak).where(Streak.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, streak: Streak) -> Streak:
        """Persist (insert or update) a streak record."""
        merged = await self.db.merge(streak)
        await self.db.commit()
        await self.db.refresh(merged)
        return merged
