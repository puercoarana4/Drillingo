import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.vocabulary import VocabularyItem
from app.repositories.progress_repo import ProgressRepository
from app.schemas.progress import (
    LessonProgressRequest,
    LessonProgressResponse,
    ProgressSummaryResponse,
    VocabularyProgressResponse,
)

# XP awarded per module type (Req 10.1)
XP_BY_MODULE = {
    "reading": 10,
    "listening": 15,
    "writing": 20,
    "speaking": 25,
}

# XP thresholds for level advancement (Req 10.3)
# 500 XP total → B2, 2000 XP total → C1
LEVEL_THRESHOLDS = [
    (2000, "C1"),
    (500, "B2"),
]


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProgressRepository(db)

    async def record_lesson_progress(
        self, user_id: uuid.UUID, data: LessonProgressRequest
    ) -> LessonProgressResponse:
        """
        Persist a completed module, award XP, and trigger level-up check.
        Returns the progress record with xp_awarded field.
        """
        # Persist the progress record
        record = await self.repo.create_lesson_progress(
            user_id=user_id,
            lesson_id=data.lesson_id,
            module_type=data.module_type,
            score=data.score,
        )

        # Award XP (Req 10.1)
        xp = XP_BY_MODULE.get(data.module_type, 0)
        new_xp = await self._add_xp(user_id, xp)

        # Check for level-up (Req 10.2)
        await self.check_level_up(user_id, new_xp)

        return LessonProgressResponse(
            id=record.id,
            user_id=record.user_id,
            lesson_id=record.lesson_id,
            module_type=record.module_type,
            score=record.score,
            completed_at=record.completed_at,
            xp_awarded=xp,
        )

    async def _add_xp(self, user_id: uuid.UUID, xp: int) -> int:
        """Add XP to user and return the new total."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.xp_total += xp
        await self.db.commit()
        await self.db.refresh(user)
        return user.xp_total

    async def check_level_up(self, user_id: uuid.UUID, new_xp_total: int) -> None:
        """
        Evaluate XP thresholds and update level_band if the user has crossed one.
        Thresholds: 500 XP → B2, 2000 XP → C1 (Req 10.2, 10.3).
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()

        new_level = user.level_band
        for threshold, level in LEVEL_THRESHOLDS:
            if new_xp_total >= threshold:
                new_level = level
                break

        if new_level != user.level_band:
            user.level_band = new_level
            await self.db.commit()

    async def get_progress_summary(
        self, user_id: uuid.UUID
    ) -> ProgressSummaryResponse:
        """Return aggregated progress metrics for the user."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()

        summary = await self.repo.get_user_summary(user_id)

        return ProgressSummaryResponse(
            user_id=user_id,
            level_band=user.level_band,
            xp_total=user.xp_total,
            reading_avg=summary.get("reading_avg"),
            listening_avg=summary.get("listening_avg"),
            writing_avg=summary.get("writing_avg"),
            speaking_avg=summary.get("speaking_avg"),
            total_lessons_completed=summary.get("total_lessons_completed", 0),
        )

    async def get_vocabulary_progress(
        self, user_id: uuid.UUID
    ) -> list[VocabularyProgressResponse]:
        """
        Return all vocabulary items the user has interacted with,
        joined with VocabularyItem details (Req 11.2, 11.3).
        """
        rows = await self.repo.get_user_vocabulary_progress(user_id)
        if not rows:
            return []

        # Fetch vocabulary item details for each row
        vocab_ids = [r.vocabulary_item_id for r in rows]
        result = await self.db.execute(
            select(VocabularyItem).where(VocabularyItem.id.in_(vocab_ids))
        )
        vocab_map = {v.id: v for v in result.scalars().all()}

        responses = []
        for row in rows:
            item = vocab_map.get(row.vocabulary_item_id)
            if item:
                responses.append(
                    VocabularyProgressResponse(
                        vocabulary_item_id=row.vocabulary_item_id,
                        term=item.term,
                        definition=item.definition,
                        example_sentence=item.example_sentence,
                        dialect_segment=item.dialect_segment,
                        level_band=item.level_band,
                        mastered=row.mastered,
                        correct_count=row.correct_count,
                        last_reviewed_at=row.last_reviewed_at,
                    )
                )
        return responses

    async def update_vocabulary_interaction(
        self,
        user_id: uuid.UUID,
        vocab_item_id: uuid.UUID,
        correct: bool,
    ) -> None:
        """
        Record a vocabulary interaction. Auto-masters after 3 correct answers (Req 11.1).
        Updates last_reviewed_at on every interaction (Req 11.4).
        """
        await self.repo.upsert_vocabulary_interaction(user_id, vocab_item_id, correct)
