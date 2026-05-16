import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import LessonProgress
from app.models.vocabulary import UserVocabulary


class ProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_lesson_progress(
        self,
        user_id: uuid.UUID,
        lesson_id: uuid.UUID,
        module_type: str,
        score: int,
    ) -> LessonProgress:
        """Persist a completed module record."""
        record = LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            module_type=module_type,
            score=score,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_all_lesson_progress(self, user_id: uuid.UUID) -> list[LessonProgress]:
        """Return all lesson_progress rows for a user (for learning path)."""
        result = await self.db.execute(
            select(LessonProgress)
            .where(LessonProgress.user_id == user_id)
            .order_by(LessonProgress.completed_at)
        )
        return list(result.scalars().all())

    async def get_user_summary(self, user_id: uuid.UUID) -> dict:
        """
        Return per-module average scores and total lesson count for a user.
        """
        result = await self.db.execute(
            select(
                LessonProgress.module_type,
                func.avg(LessonProgress.score).label("avg_score"),
                func.count(LessonProgress.id).label("count"),
            )
            .where(LessonProgress.user_id == user_id)
            .group_by(LessonProgress.module_type)
        )
        rows = result.all()

        summary: dict = {
            "reading_avg": None,
            "listening_avg": None,
            "writing_avg": None,
            "speaking_avg": None,
            "total_lessons_completed": 0,
        }
        for row in rows:
            key = f"{row.module_type}_avg"
            summary[key] = float(row.avg_score)
            summary["total_lessons_completed"] += row.count

        return summary

    async def get_user_vocabulary_progress(
        self, user_id: uuid.UUID
    ) -> list[UserVocabulary]:
        """Return all UserVocabulary rows for a user."""
        result = await self.db.execute(
            select(UserVocabulary).where(UserVocabulary.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_vocabulary_item(
        self, user_id: uuid.UUID, vocab_item_id: uuid.UUID
    ) -> Optional[UserVocabulary]:
        """Return a single UserVocabulary row, or None."""
        result = await self.db.execute(
            select(UserVocabulary).where(
                UserVocabulary.user_id == user_id,
                UserVocabulary.vocabulary_item_id == vocab_item_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_vocabulary_interaction(
        self,
        user_id: uuid.UUID,
        vocab_item_id: uuid.UUID,
        correct: bool,
    ) -> UserVocabulary:
        """
        Increment correct_count if correct, update last_reviewed_at.
        Creates the row if it doesn't exist yet.
        """
        row = await self.get_user_vocabulary_item(user_id, vocab_item_id)
        if row is None:
            row = UserVocabulary(
                user_id=user_id,
                vocabulary_item_id=vocab_item_id,
                correct_count=1 if correct else 0,
                mastered=False,
                last_reviewed_at=datetime.now(timezone.utc),
            )
            self.db.add(row)
        else:
            if correct:
                row.correct_count += 1
            row.last_reviewed_at = datetime.now(timezone.utc)
            # Auto-master after 3 correct answers (Req 11.1)
            if row.correct_count >= 3:
                row.mastered = True

        await self.db.commit()
        await self.db.refresh(row)
        return row
